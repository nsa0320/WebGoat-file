pipeline {
    agent any

    environment {
        ECR_REGISTRY = "341162387145.dkr.ecr.ap-northeast-2.amazonaws.com"
        APP_REPO_NAME = "nsa"
        AWS_REGION = "ap-northeast-2"
        IMAGE_URI = "${ECR_REGISTRY}/${APP_REPO_NAME}:latest"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'develop',
                    url: 'https://github.com/nsa0320/WebGoat-file.git',
                    credentialsId: '1' // ✅ GitHub 자격증명
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
                    docker build --force-rm -t $IMAGE_URI .
                '''
            }
        }

        stage('Login to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'ecr-login']]) {
                    sh '''
                        aws ecr get-login-password --region $AWS_REGION \
                        | docker login --username AWS --password-stdin $ECR_REGISTRY
                    '''
                }
            }
        }

        stage('Push to ECR') {
            steps {
                sh 'docker push $IMAGE_URI'
            }
        }

        stage('Generate ECS Task and AppSpec') {
            steps {
                script {
                    writeFile file: 'taskdef.json', text: """
{
  "family": "webgoat-taskdef",
  "executionRoleArn": "arn:aws:iam::341162387145:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "containerDefinitions": [{
    "name": "webgoat",
    "image": "$IMAGE_URI",
    "essential": true,
    "portMappings": [{
      "containerPort": 8080,
      "protocol": "tcp"
    }]
  }],
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024"
}
                    """

                    writeFile file: 'appspec.yaml', text: """
version: 0.0
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: webgoat-taskdef
        LoadBalancerInfo:
          ContainerName: webgoat
          ContainerPort: 8080
                    """
                }
            }
        }

        stage('Deploy to ECS') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'ecr-login']]) {
                    sh '''
                        aws ecs register-task-definition --cli-input-json file://taskdef.json

                        aws deploy create-deployment \
                          --application-name webgoat-app \
                          --deployment-group-name webgoat-deploy-group \
                          --deployment-config-name CodeDeployDefault.ECSAllAtOnce \
                          --revision type=AppSpecContent,appSpecContent="{\\"content\\": \\"$(base64 appspec.yaml | tr -d '\\n')\\"}"
                    '''
                }
            }
        }
    }

    post {
        always {
            echo '🧼 Cleaning up local Docker images...'
            sh 'docker image prune -af'
        }
    }
}
