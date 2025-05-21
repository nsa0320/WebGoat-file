pipeline {
    agent any

    environment {
        ECR_REGISTRY = "341162387145.dkr.ecr.ap-northeast-2.amazonaws.com"
        APP_REPO_NAME = "nsa"
        AWS_REGION = "ap-northeast-2"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'develop',
                    url: 'https://github.com/nsa0320/WebGoat.git',
                    credentialsId: '1'  
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
                    docker build --force-rm \
                    -t $ECR_REGISTRY/$APP_REPO_NAME:latest .
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
                sh 'docker push $ECR_REGISTRY/$APP_REPO_NAME:latest'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up Docker images...'
            sh 'docker image prune -af'
        }
    }
}
