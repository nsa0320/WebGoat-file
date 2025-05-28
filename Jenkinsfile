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

        stage('Run Semgrep on SqlInjectionLesson only') {
            steps {
                sshagent(["$SEMGREP_KEY"]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no $SEMGREP_SERVER '
                          rm -rf ~/code && mkdir -p ~/code
                        '
                        scp -o StrictHostKeyChecking=no src/main/java/org/owasp/webgoat/sqlinjection/SqlInjectionLesson.java $SEMGREP_SERVER:~/code/
                        ssh -o StrictHostKeyChecking=no $SEMGREP_SERVER '
                          docker run --rm -v ~/code:/src semgrep/semgrep semgrep scan --config auto --json > ~/code/result.json
                        '
                        scp -o StrictHostKeyChecking=no $SEMGREP_SERVER:~/code/result.json .
                    """
                }
            }
        }

        stage('Generate & Publish Semgrep Report') {
            steps {
                sh 'python3 json_to_html.py'

                publishHTML(target: [
                    reportName : 'Semgrep Report - SqlInjectionLesson Only',
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
            echo '✅ Semgrep scan for SqlInjectionLesson completed!'
        }
        failure {
            echo '❌ Semgrep scan failed.'
        }
    }
}
