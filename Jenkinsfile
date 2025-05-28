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

        stage('Run Semgrep (full scan)') {
            steps {
                sh '''
                    rm -rf semgrep-output || true
                    mkdir -p semgrep-output

                    docker run --rm \
                      -v "$PWD":/src \
                      -v "$PWD/semgrep-output":/output \
                      ${SEMGREP_IMAGE} \
                      semgrep scan --config auto /src --json --output /output/result.json
                '''
            }
        }

        stage('Generate & Publish Semgrep Report') {
            steps {
                sh '''
                    python3 json_to_html.py semgrep-output/result.json > semgrep-output/report.html
                '''

                publishHTML(target: [
                    reportName : 'Semgrep Report - full scan',
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
            echo '✅ Semgrep full scan completed!'
        }
        failure {
            echo '❌ Semgrep scan failed!'
        }
    }
}
