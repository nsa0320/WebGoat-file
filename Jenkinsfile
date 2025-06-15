pipeline {
    agent any

    environment {
        JAVA_HOME = "/usr/lib/jvm/java-17-amazon-corretto.x86_64"
        PATH = "${env.JAVA_HOME}/bin:${env.PATH}"
        REGION = "ap-northeast-2"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('🧪 SonarQube Analysis') {
            steps {
                script{
                    load 'components/sonarqube_analysis.groovy'
                }
            }
        }

        stage('🔨 Build JAR') {
            steps {
                sh 'components/scripts/Build_JAR.sh'
            }
        }

        stage('🐳 Docker Build') {
            steps {
                sh 'components/scripts/Docker_Build.sh'
            }
        }

        stage('🔐 ECR Login') {
            steps {
                sh 'components/scripts/ECR_Login.sh'
            }
        }

        stage('🚀 Push to ECR') {
            steps {
                sh 'components/scripts/Push_to_ECR.sh'
            }
        }

        stage('🧩 Generate taskdef.json') {
            steps {
                script {
                    def runTaskDefGen = load 'components/functions/generateTaskDef.groovy'
                    runTaskDefGen(env)
                }
            }
        }

        stage('📄 Generate appspec.yaml') {
            steps {
                script {
                    def runAppSpecGen = load 'components/functions/generateAppspecAndWrite.groovy'
                    runAppSpecGen(env.REGION)
                }
            }
        }

        stage('📦 Bundle for CodeDeploy') {
            steps {
                sh 'components/scripts/Bundle_for_CodeDeploy.sh'
            }
        }

        stage('🚀 Deploy via CodeDeploy') {
            steps {
                sh 'components/scripts/Deploy_via_CodeDeploy.sh'
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
