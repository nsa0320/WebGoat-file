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

        stage('CodeQL Analysis') {
            steps {
                withCodeQL(codeql: 'CodeQL 2.21.4') {
                    sh '''
                        rm -rf codeql-db codeql-report
                        codeql database create codeql-db \
                          --language=java \
                          --command="mvn clean compile -DskipTests" \
                          --source-root=.
                        
                        mkdir -p codeql-report
                        codeql database analyze codeql-db \
                          /opt/codeql-repo/java/ql/src/codeql-suites/java-code-scanning.qls \
                          --format=sarifv2.1.0 \
                          --output=codeql-report/codeql-result.sarif \
                          --ram=3000
                    '''
                }
            }
        }

        stage('Archive SARIF') {
            steps {
                archiveArtifacts artifacts: 'codeql-report/codeql-result.sarif', fingerprint: true
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up...'
            sh 'rm -rf codeql-db'
        }
        success {
            echo '✅ CodeQL scan completed and SARIF archived!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}

