pipeline {
    agent any

    environment {
        BEST_R2 = credentials('best-r2')
        BEST_MSE = credentials('best-mse')
        IMAGE_NAME = "2022bcs0090arshabelkumar/wine_predict_2022bcs0090"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                . venv/bin/activate
                python scripts/train.py
                '''
            }
        }

        stage('Read Metrics') {
            steps {
                script {
                    env.CURRENT_R2 = sh(
                        script: "jq '.r2' app/artifacts/results/metrics.json",
                        returnStdout: true
                    ).trim()

                    env.CURRENT_MSE = sh(
                        script: "jq '.mse' app/artifacts/results/metrics.json",
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage('Compare Metrics') {
            steps {
                script {

                    def betterR2 = (
                        sh(script: "echo '${CURRENT_R2} > ${BEST_R2}' | bc",
                           returnStdout: true).trim() == "1"
                    )

                    def betterMSE = (
                        sh(script: "echo '${CURRENT_MSE} < ${BEST_MSE}' | bc",
                           returnStdout: true).trim() == "1"
                    )

                    env.IS_BETTER = (betterR2 && betterMSE).toString()
                }
            }
        }

        stage('Build Docker Image') {
            when {
                expression { env.IS_BETTER == "true" }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    docker login -u $DOCKER_USER -p $DOCKER_PASS
                    docker build -t $IMAGE_NAME:${BUILD_NUMBER} .
                    docker tag $IMAGE_NAME:${BUILD_NUMBER} $IMAGE_NAME:latest
                    '''
                }
            }
        }

        stage('Push Docker Image') {
            when {
                expression { env.IS_BETTER == "true" }
            }
            steps {
                sh '''
                docker push $IMAGE_NAME:${BUILD_NUMBER}
                docker push $IMAGE_NAME:latest
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'app/artifacts/**'
        }
    }
}
