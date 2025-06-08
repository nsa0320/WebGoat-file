pipeline {
    agent any

    environment {
        ECR_REPO = "535052053335.dkr.ecr.ap-northeast-2.amazonaws.com/wh_1/devpos"
        IMAGE_TAG = "latest"
        JAVA_HOME = "/usr/lib/jvm/java-17-amazon-corretto.x86_64"
        PATH = "${env.JAVA_HOME}/bin:${env.PATH}"
        S3_BUCKET = "webgoat-codedeploy-bucket-soobin"
        DEPLOY_APP = "webgoat-cd-app"
        DEPLOY_GROUP = "webgoat-deploy-group"
        REGION = "ap-northeast-2"
        BUNDLE = "deploy2.zip"
        SONARQUBE_ENV = "WH_sonarqube"
    }

    stages {
        stage('Checkout') {
            // 현재 jenkins job이 연결된 git 저장소를 클론해오는 단계
            // Jenkins에서는 scm (source code management)을 통해 소스코드를 가져옴
            // checkout scm은 job이 연동된 git 저장소의 코드를 가져온다는 것
            steps {
                checkout scm
            }
        }

        // 웹훅 다시 설정
        // sonarQube 규칙 설정
        // 인스턴스 바꿔서 시작 경로수정..
        stage('🧪 SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    sh '''
                    /opt/sonar-scanner/bin/sonar-scanner \
                        -Dsonar.projectKey=webgoat \
                        -Dsonar.sources=. \
                        -Dsonar.java.binaries=target/classes
                    '''
                }
            }
        }

        stage('🔨 Build JAR') {
            // Maven으로 WebGoat 애플리케이션을 빌드해서 .jar 파일을 만듦
            // mvn = Maven 명령어
            // clean = 이전 빌드 산출물 삭제
            // package = .jar 나 .war 파일을 생성 -> 파일 이름은 pom.xml에 정의된 값으로 자동 생성됨
            // -DskipTests = 테스트 생략하고 빠르게 빌드만
            // 이 단계가 java프로젝트를 실행 가능한 결과물로 만드는 핵심임
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }

        stage('🐳 Docker Build') {
            // 방금 만든 .jar 파일을 도커 컨테이너 이미지로 만듦
            // 즉, WebGoat 애플리케이션을 Docker 안에 넣음
            // 다시 말하면, .jar을 컨테이너로 포장하는 것!
            steps {
                sh '''
                docker build -t $ECR_REPO:$IMAGE_TAG .
                '''
            }
        }

        stage('🔐 ECR Login') {
            steps {
                sh '''
                aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPO
                '''
            }
        }

        stage('🚀 Push to ECR') {
            steps {
                sh 'docker push $ECR_REPO:$IMAGE_TAG'
            }
        }

        stage('🧩 Generate taskdef.json') {
            steps {
                script {
                    def taskdef = """{
  "family": "webgoat-task-def",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "webgoat",
      "image": "${ECR_REPO}:${IMAGE_TAG}",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ]
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::535052053335:role/ecsTaskExecutionRole"
}"""
                    writeFile file: 'taskdef.json', text: taskdef
                }
            }
        }

        stage('📄 Generate appspec.yaml') {
            steps {
                script {
                    def taskDefArn = sh(
                        script: "aws ecs register-task-definition --cli-input-json file://taskdef.json --query 'taskDefinition.taskDefinitionArn' --region $REGION --output text",
                        returnStdout: true
                    ).trim()

                    def appspec = """version: 1
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: "${taskDefArn}"
        LoadBalancerInfo:
          ContainerName: "webgoat"
          ContainerPort: 8080
"""
                    writeFile file: 'appspec.yaml', text: appspec
                }
            }
        }

        stage('📦 Bundle for CodeDeploy') {
            steps {
                sh 'zip -r $BUNDLE appspec.yaml Dockerfile taskdef.json'
            }
        }

        stage('🚀 Deploy via CodeDeploy') {
            steps {
                sh '''
                aws s3 cp $BUNDLE s3://$S3_BUCKET/$BUNDLE --region $REGION

                aws deploy create-deployment \
                  --application-name $DEPLOY_APP \
                  --deployment-group-name $DEPLOY_GROUP \
                  --deployment-config-name CodeDeployDefault.ECSAllAtOnce \
                  --s3-location bucket=$S3_BUCKET,bundleType=zip,key=$BUNDLE \
                  --region $REGION
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Successfully built, pushed, and deployed!"
        }
        failure {
            echo "❌ Build or deployment failed. Check logs!"
        }
    }
}
