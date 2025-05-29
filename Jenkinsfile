pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-northeast-2'
        AWS_ACCESS_KEY_ID = credentials('ecr-login')
        AWS_SECRET_ACCESS_KEY = credentials('ecr-login')
        ECR_REGISTRY = '341162387145.dkr.ecr.ap-northeast-2.amazonaws.com'
        APP_REPO_NAME = 'nsa'
        S3_BUCKET = 'webgoat-nsa'
        CONTAINER_NAME = 'dummy'
        CONTAINER_PORT = 8080
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'develop',
                    url: 'https://github.com/nsa0320/WebGoat-file.git',
                    credentialsId: '1'
            }
        }

        stage('Semgrep Analysis via Lambda') {
            steps {
                sh '''
                    echo "[📦] 소스코드 압축 중..."
                    zip -r source.zip . -x "*.git*" "*.idea*" "target/*"

                    echo "[☁️] S3에 업로드 중..."
                    aws s3 cp source.zip s3://$S3_BUCKET/source.zip

                    echo "[🚀] Lambda로 Semgrep 실행 요청 중..."
                    aws lambda invoke \
                      --function-name trigger-semgrep-analysis-ssm \
                      --payload '{"s3_key":"source.zip"}' \
                      --region $AWS_REGION \
                      --cli-binary-format raw-in-base64-out \
                      lambda_output.json

                    echo "[📄] Lambda 응답 내용:"
                    cat lambda_output.json
                '''
            }
        }

        stage('Build JAR') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build --force-rm -t $ECR_REGISTRY/$APP_REPO_NAME:latest .
                '''
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up local Docker images...'
            sh 'docker image prune -af'
        }
        success {
            echo '✅ Semgrep + Build + Docker succeeded!'
        }
        failure {
            echo '❌ Pipeline failed. Check the logs above.'
        }
    }
}
