pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-northeast-2'
        AWS_ACCESS_KEY_ID = credentials('ecr-login')
        AWS_SECRET_ACCESS_KEY = credentials('ecr-login')
        ECR_REGISTRY = '341162387145.dkr.ecr.ap-northeast-2.amazonaws.com'
        APP_REPO_NAME = 'nsa'
        S3_BUCKET = 'webgoat-nsa'
        DEPLOY_APP = 'webgoat-app'
        DEPLOY_GROUP = 'webgoat-deploy-group'
        BUNDLE_NAME = 'webgoat-deploy.zip'
        CONTAINER_NAME = 'dummy'
        CONTAINER_PORT = 8080
        TASK_EXEC_ROLE = 'arn:aws:iam::341162387145:role/ecsTaskExecutionRole'
        ECS_SERVICE_NAME = 'webgoat-dummy-task-service-rfvbclnr'
        SEMGREP_SERVER = 'ec2-user@13.125.229.113'
        SEMGREP_KEY = 'semgrep-fix-key'
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
                sh 'docker build --force-rm -t $ECR_REGISTRY/$APP_REPO_NAME:latest .'
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

        // ✅ Semgrep 분석 스테이지
        stage('Run Semgrep Security Scan') {
            steps {
                sshagent(["$SEMGREP_KEY"]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no $SEMGREP_SERVER '
                          rm -rf ~/code && mkdir -p ~/code
                        '
                        scp -o StrictHostKeyChecking=no -r * $SEMGREP_SERVER:~/code
                        ssh -o StrictHostKeyChecking=no $SEMGREP_SERVER '
                          docker run --rm -v ~/code:/src semgrep/semgrep semgrep scan --config auto --json > ~/code/result.json
                        '
                        scp -o StrictHostKeyChecking=no $SEMGREP_SERVER:~/code/result.json .
                    """
                }
            }
        }

        // ✅ HTML 리포트 생성 + Jenkins 리포트 표시
        stage('Generate & Publish Semgrep Report') {
            steps {
                sh 'python3 json_to_html.py'

                publishHTML(target: [
                    reportName : 'Semgrep Report',
                    reportDir  : '.',
                    reportFiles: 'report.html',
                    keepAll    : true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])
            }
        }

        stage('Generate taskdef.json and appspec.yaml') {
            steps {
                script {
                    def imageUri = "${ECR_REGISTRY}/${APP_REPO_NAME}:latest"

                    def taskdef = """{
  "family": "webgoat-taskdef",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "${CONTAINER_NAME}",
      "image": "${imageUri}",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "portMappings": [
        {
          "containerPort": ${CONTAINER_PORT},
          "protocol": "tcp"
        }
      ]
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "${TASK_EXEC_ROLE}"
}"""
                    writeFile file: 'taskdef.json', text: taskdef

                    def taskDefArn = sh(
                        script: "aws ecs register-task-definition --cli-input-json file://taskdef.json --query 'taskDefinition.taskDefinitionArn' --region $AWS_REGION --output text",
                        returnStdout: true
                    ).trim()

                    def appspec = """version: 1
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: "${taskDefArn}"
        LoadBalancerInfo:
          ContainerName: "${CONTAINER_NAME}"
          ContainerPort: ${CONTAINER_PORT}
        PlatformVersion: "LATEST"
"""
                    writeFile file: 'appspec.yaml', text: appspec
                }
            }
        }

        stage('Zip and Upload for CodeDeploy') {
            steps {
                sh '''
                    zip $BUNDLE_NAME appspec.yaml taskdef.json
                    aws s3 cp $BUNDLE_NAME s3://$S3_BUCKET/$BUNDLE_NAME --region $AWS_REGION
                '''
            }
        }

        stage('Trigger CodeDeploy') {
            steps {
                sh '''
                    aws deploy create-deployment \
                      --application-name $DEPLOY_APP \
                      --deployment-group-name $DEPLOY_GROUP \
                      --deployment-config-name CodeDeployDefault.ECSAllAtOnce \
                      --s3-location bucket=$S3_BUCKET,bundleType=zip,key=$BUNDLE_NAME \
                      --region $AWS_REGION
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
            echo '✅ Deployment succeeded!'
        }
        failure {
            echo '❌ Deployment failed. Check logs!'
        }
    }
}
