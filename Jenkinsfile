pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-northeast-2'
        AWS_ACCESS_KEY_ID = credentials('ecr-login')
        AWS_SECRET_ACCESS_KEY = credentials('ecr-login')
        ECR_REGISTRY = '341162387145.dkr.ecr.ap-northeast-2.amazonaws.com'
        APP_REPO_NAME = 'nsa'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'develop',
                    url: 'https://github.com/nsa0320/WebGoat-file.git',
                    credentialsId: '1'
            }
        }

        stage('Build JAR') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }

        stage('Run CodeQL Create DB') {
            steps {
                sh '''
                    rm -rf codeql-db
                    mkdir -p codeql-db
                    /opt/codeql/codeql database create codeql-db \
                      --language=java \
                      --command="mvn clean compile -DskipTests" \
                      --source-root=.
                '''
            }
        }

        stage('Run CodeQL Analysis') {
            steps {
                sh '''
                    mkdir -p codeql-report
                    /opt/codeql/codeql database analyze codeql-db \
                      /opt/codeql-repo/java/ql/src/codeql-suites/java-code-scanning.qls \
                      --format=sarifv2.1.0 \
                      --output=codeql-report/codeql-result.sarif \
                      --ram=3000
                '''
            }
        }

        


        stage('Build Docker Image') {
            steps {
                sh 'docker build --force-rm -t $ECR_REGISTRY/$APP_REPO_NAME:latest .'
            }
        }

        stage('Login to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region $AWS_REGION \
                    | docker login --username AWS --password-stdin $ECR_REGISTRY
                '''
            }
        }stage('Generate & Publish CodeQL Report') {
    steps {
        sh '''
            export PATH=$PATH:/var/lib/jenkins/.local/bin
            python3 -m pip install --quiet --disable-pip-version-check --user sarif-tools
            mkdir -p codeql-html
            python3 -m sarif.tools.sarif_to_html codeql-report/codeql-result.sarif > codeql-html/index.html
        '''
        publishHTML(target: [
            reportName: 'CodeQL Report',
            reportDir: 'codeql-html',
            reportFiles: 'index.html',
            keepAll: true,
            alwaysLinkToLastBuild: true,
            allowMissing: false
        ])
    }
}


        stage('Push to ECR') {
            steps {
                sh 'docker push $ECR_REGISTRY/$APP_REPO_NAME:latest'
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up local Docker images...'
            sh 'docker image prune -af'
        }
        success {
            echo '✅ Build, scan, and push to ECR completed!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs!'
        }
    }
}
