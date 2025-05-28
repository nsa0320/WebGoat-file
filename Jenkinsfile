pipeline {
    agent any

    environment {
        SEMGREP_IMAGE = 'semgrep/semgrep'  // 공식 Semgrep Docker 이미지
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'develop',
                    url: 'https://github.com/nsa0320/WebGoat-file.git',
                    credentialsId: '1'
            }
        }

       stage('Run Semgrep (local, limited path)') {
    steps {
        sh '''
            rm -rf semgrep-output || true
            mkdir -p semgrep-output

            docker run --rm \
              -v "$(pwd)/src/main/java/org/owasp/webgoat/lessons/sqlinjection":/src \
              -v "$(pwd)/semgrep-output":/output \
              semgrep/semgrep \
              semgrep scan --config auto /src --json > /output/result.json
        '''
    }
}

        stage('Generate & Publish Semgrep Report') {
            steps {
                sh '''
                    python3 json_to_html.py semgrep-output/result.json > semgrep-output/report.html
                '''

                publishHTML(target: [
                    reportName : 'Semgrep Report - sqlinjection only',
                    reportDir  : 'semgrep-output',
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
            echo '✅ Semgrep local scan completed!'
        }
        failure {
            echo '❌ Semgrep scan failed!'
        }
    }
}
