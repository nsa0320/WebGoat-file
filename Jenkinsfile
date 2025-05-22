pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-northeast-2'
        AWS_ACCESS_KEY_ID = credentials('ecr-login')
        AWS_SECRET_ACCESS_KEY = credentials('ecr-login')
        ECR_REGISTRY = '341162387145.dkr.ecr.ap-northeast-2.amazonaws.com'
        APP_REPO_NAME = 'nsa'
        S3_BUCKET = 'codedeploy-files-nsa'
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

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build --force-rm -t $ECR_REGISTRY/$APP_REPO_NAME:latest .
                '''
            }
        }

        stage('Login to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                sh 'docker push $ECR_REGISTRY/$APP_REPO_NAME:latest'
            }
        }

        stage('Upload Image Definitions to S3') {
            steps {
                script {
                    def imageUri = "${ECR_REGISTRY}/${APP_REPO_NAME}:latest"
                    writeFile file: 'imagedefinitions.json', text: """[
  {
    "name": "webgoat",
    "imageUri": "${imageUri}"
  }
]"""
                }
                sh '''
                    aws s3 cp imagedefinitions.json s3://codedeploy-files-nsa/imagedefinitions.json
                '''
                sleep(time: 3, unit: 'SECONDS')
            }
        }

        stage('Trigger CodeDeploy') {
            steps {
                sh '''
                    aws deploy create-deployment \
                      --application-name webgoat-app \
                      --deployment-group-name webgoat-deploy-group \
                      --deployment-config-name CodeDeployDefault.ECSAllAtOnce \
                      --s3-location bucket=codedeploy-files-nsa,key=webgoat-deploy.zip,bundleType=zip \
                      --region $AWS_REGION
                '''
            }
        }
    }

    post {
        always {
            echo '🧼 Cleaning up Docker images...'
            sh 'docker image prune -af'
        }
    }
}
