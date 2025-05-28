pipeline {
    agent any

    environment {
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

        // ✅ Semgrep 특정 경로 스캔
        stage('Run Semgrep on hijacksession only') {
            steps {
                sshagent(["$SEMGREP_KEY"]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no $SEMGREP_SERVER '
                          rm -rf ~/code && mkdir -p ~/code
                        '
                        scp -o StrictHostKeyChecking=no -r src/src/main/resources/lessons/hijacksession $SEMGREP_SERVER:~/code/
                        ssh -o StrictHostKeyChecking=no $SEMGREP_SERVER '
                          docker run --rm -v ~/code:/src semgrep/semgrep semgrep scan --config auto --json > ~/code/result.json
                        '
                        scp -o StrictHostKeyChecking=no $SEMGREP_SERVER:~/code/result.json .
                    """
                }
            }
        }

        // ✅ HTML 변환 및 리포트 출력
        stage('Generate & Publish Semgrep Report') {
            steps {
                sh 'python3 json_to_html.py'

                publishHTML(target: [
                    reportName : 'Semgrep Report - hijacksession only',
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
        success {
            echo '✅ Semgrep scan (limited path) succeeded!'
        }
        failure {
            echo '❌ Semgrep scan failed.'
        }
    }
}

