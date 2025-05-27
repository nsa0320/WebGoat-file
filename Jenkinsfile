pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-northeast-2'
        AWS_ACCESS_KEY_ID = credentials('ecr-login')
        AWS_SECRET_ACCESS_KEY = credentials('ecr-login')
        ECR_REGISTRY = '341162387145.dkr.ecr.ap-northeast-2.amazonaws.com'
        APP_REPO_NAME = 'nsa'
        S3_BUCKET = 'webgoat-nsa1'
        DEPLOY_APP = 'webgoat-app'
        DEPLOY_GROUP = 'webgoat-deploy-group'
        BUNDLE_NAME = 'webgoat-deploy.zip'
        CONTAINER_NAME = 'dummy'
        CONTAINER_PORT = 8080
        TASK_EXEC_ROLE = 'arn:aws:iam::341162387145:role/ecsTaskExecutionRole'

        GIT_COMMIT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
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

        // ✅ 추가: CodeQL용 소스코드 압축 및 S3 업로드
        stage('Upload Source for CodeQL') {
            steps {
                sh '''
                    echo "📦 압축: src/ → source-${GIT_COMMIT}.tar.gz"
                    echo "application-secret.properties" > .tarignore
                    tar czf source.tar.gz --exclude-from=.tarignore src/
                    mv source.tar.gz source-${GIT_COMMIT}.tar.gz

                    echo "☁️ S3 업로드 중..."
                    aws s3 cp source-${GIT_COMMIT}.tar.gz s3://webgoat-nsa1/code/source-${GIT_COMMIT}.tar.gz
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build --force-rm -t $ECR_REGISTRY/$APP_REPO_NAME:latest .
                '''
            }
        }

        // 나머지 Login to ECR ~ Trigger CodeDeploy 등은 그대로 유지됨...
    }

    post {
        always {
            echo '🧹 Cleaning up local Docker images...'
            sh 'docker image prune -af'
        }
        success {
            echo '✅ Deployment succeeded!'
        }
        failure {
            echo '❌ Deployment failed. Check logs!'
        }
    }
}
