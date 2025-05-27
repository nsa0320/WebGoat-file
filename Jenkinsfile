pipeline {
    agent any

    environment {
        AWS_REGION = "ap-northeast-2"
        ECR_REGISTRY = "341162387145.dkr.ecr.ap-northeast-2.amazonaws.com"
        APP_REPO_NAME = "nsa"

        // AWS 자격증명
        AWS_ACCESS_KEY_ID = credentials('aws-access-key')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key')
        
        // 현재 커밋 ID를 환경변수로 저장
        GIT_COMMIT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'develop',
                    credentialsId: '1',
                    url: 'https://github.com/nsa0320/WebGoat.git'
            }
        }

        stage('Build JAR') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }

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
                    docker build --force-rm \
                    -t $ECR_REGISTRY/$APP_REPO_NAME:${GIT_COMMIT} .
                '''
            }
        }

        stage('Login to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region $AWS_REGION \
                    | docker login --username AWS --password-stdin $ECR_REGISTRY
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                sh 'docker push $ECR_REGISTRY/$APP_REPO_NAME:${GIT_COMMIT}'
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up Docker images...'
            sh 'docker image prune -af'
        }
    }
}
