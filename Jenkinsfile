pipeline {
    agent any

    environment {
        CODEQL_PATH = '/opt/codeql/codeql'
        CODEQL_REPO = '/opt/codeql-repo'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'develop',
                    url: 'https://github.com/nsa0320/WebGoat-file.git',
                    credentialsId: '1'
            }
        }

        stage('Build JAR for CodeQL DB') {
            steps {
                sh 'mvn clean compile -DskipTests'
            }
        }

        stage('Create CodeQL Database') {
            steps {
                sh '''
                    rm -rf codeql-db
                    mkdir -p codeql-db
                    ${CODEQL_PATH} database create codeql-db \
                      --language=java \
                      --command="mvn clean compile -DskipTests" \
                      --source-root=.
                '''
            }
        }

        stage('Analyze with CodeQL') {
            steps {
                sh '''
                    mkdir -p codeql-report
                    ${CODEQL_PATH} database analyze codeql-db \
                      ${CODEQL_REPO}/java/ql/src/codeql-suites/java-code-scanning.qls \
                      --format=sarifv2.1.0 \
                      --output=codeql-report/codeql-result.sarif \
                      --ram=3000
                '''
            }
        }

        stage('Generate HTML Report') {
            steps {
                sh '''
                    export PATH=$PATH:/var/lib/jenkins/.local/bin
                    python3 -m pip install --user --quiet --disable-pip-version-check sarif-tools || true
                    mkdir -p codeql-html
                    python3 -m sarif.tools.sarif_to_html codeql-report/codeql-result.sarif > codeql-html/index.html
                '''
            }
        }

        stage('Publish Report') {
            steps {
                publishHTML(target: [
                    reportName : 'CodeQL Report',
                    reportDir  : 'codeql-html',
                    reportFiles: 'index.html',
                    keepAll    : true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])
            }
        }
    }

    post {
        success {
            echo '✅ CodeQL 분석과 리포트 생성 완료!'
        }
        failure {
            echo '❌ 실패! 로그 확인 필요.'
        }
    }
}
