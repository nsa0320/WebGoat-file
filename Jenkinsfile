pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-northeast-2'
        AWS_ACCESS_KEY_ID = credentials('ecr-login')
        AWS_SECRET_ACCESS_KEY = credentials('ecr-login')
        S3_BUCKET = 'webgoat-nsa'
        SEMGREP_SERVER = 'ec2-user@13.125.229.113'
        SEMGREP_KEY = 'semgrep-fix-key'
    }

    stages {
        stage('Checkout') {
            steps {
                deleteDir()
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

        stage('Run Semgrep Security Scan via SSH') {
            steps {
                sshagent(["$SEMGREP_KEY"]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no $SEMGREP_SERVER '
                          rm -rf ~/code && mkdir -p ~/code
                        '
                        scp -o StrictHostKeyChecking=no -r * $SEMGREP_SERVER:~/code
                        ssh -o StrictHostKeyChecking=no $SEMGREP_SERVER '
                          docker run --rm -v ~/code:/src semgrep/semgrep semgrep scan --config auto --json > ~/code/result.json &&
                          aws s3 cp ~/code/result.json s3://$S3_BUCKET/semgrep/result.json
                        '
                    """
                }
            }
        }

        stage('Wait for Semgrep Result on S3') {
            steps {
                script {
                    echo "[⏳] S3에 Semgrep 결과가 업로드될 때까지 대기 중..."
                    def retries = 60
                    def interval = 5
                    def found = false

                    for (int i = 0; i < retries; i++) {
                        def status = sh(
                            script: "aws s3 ls s3://$S3_BUCKET/semgrep/result.json",
                            returnStatus: true
                        )
                        if (status == 0) {
                            echo "[✅] result.json 확인 완료!"
                            found = true
                            break
                        }
                        echo "[⏱️] 아직 result.json 없음. ${interval}초 후 재시도..."
                        sleep interval
                    }

                    if (!found) {
                        error("❌ semgrep result.json을 S3에서 ${retries * interval}초 동안 찾지 못했습니다.")
                    }
                }
            }
        }

        stage('Download & Publish Semgrep Report') {
            steps {
                sh """
                    echo "[📥] S3에서 result.json 다운로드..."
                    aws s3 cp s3://$S3_BUCKET/semgrep/result.json result.json

                    echo "[📄] HTML 리포트 생성..."
                    python3 json_to_html.py
                """

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
    }

    post {
        always {
            echo '🧹 Cleaning up local Docker images...'
            sh 'docker image prune -af || true'
        }
        success {
            echo '✅ Semgrep 분석 및 JAR 빌드 완료!'
        }
        failure {
            echo '❌ 실패. 로그 확인 필요.'
        }
    }
}
