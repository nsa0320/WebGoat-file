pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-northeast-2'
        AWS_ACCESS_KEY_ID = credentials('ecr-login')
        AWS_SECRET_ACCESS_KEY = credentials('ecr-login')
        S3_BUCKET = 'webgoat-nsa'
        LAMBDA_NAME = 'trigger-semgrep-analysis-ssm'
    }

    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                git branch: 'develop',
                    url: 'https://github.com/nsa0320/javulna.git',
                    credentialsId: '1'
            }
        }

        stage('Upload and Trigger Semgrep via Lambda') {
            steps {
                script {
                    def START = System.currentTimeMillis()

                    sh '''
                        echo "[📦] 소스코드 압축 중..."
                        zip -r source.zip . -x "*.git*" "*.idea*" "target/*"

                        echo "[☁️] S3에 업로드 중..."
                        aws s3 cp source.zip s3://$S3_BUCKET/source.zip

                        echo "[🚀] Lambda로 Semgrep 실행 요청 중..."
                        aws lambda invoke \
                          --function-name $LAMBDA_NAME \
                          --payload '{"s3_key":"source.zip"}' \
                          --region $AWS_REGION \
                          --cli-binary-format raw-in-base64-out \
                          lambda_output.json

                        echo "[📄] Lambda 응답 내용:"
                        cat lambda_output.json
                    '''

                    def END = System.currentTimeMillis()
                    echo "⏱️ Lambda 요청 소요 시간: ${(END - START) / 1000.0}초"
                }
            }
        }

        stage('Download & Visualize Semgrep Result') {
            steps {
                sh '''
                    echo "[📥] S3에서 결과 파일 다운로드..."
                    aws s3 cp s3://$S3_BUCKET/semgrep-result.json semgrep-result.json
                    aws s3 cp s3://$S3_BUCKET/semgrep-duration.txt semgrep-duration.txt

                    echo "[📄] HTML 리포트 생성 중..."
                    python3 create_semgrep_report.py
                '''

                script {
                    def duration = readFile('semgrep-duration.txt').trim()
                    echo "⏱️ 실제 Semgrep 분석 소요 시간: ${duration}초"
                }

                publishHTML(target: [
                    reportName : 'Semgrep Report',
                    reportDir  : '.',
                    reportFiles: 'semgrep-report.html',
                    keepAll    : true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])
            }
        }

        stage('Build JAR') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up local Docker images...'
            sh 'docker image prune -af || true'
        }
        success {
            echo '✅ Semgrep 분석, 시각화 및 JAR 빌드 완료!'
        }
        failure {
            echo '❌ 실패. 로그 확인 필요.'
        }
    }
}
