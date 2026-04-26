pipeline {
    agent any
    
    environment {
        DOCKER_CRED = credentials('docker-hub-credentials')
        DOCKER_IMAGE = 'houdanasr/energy-scaler'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo '✅ Code récupéré'
            }
        }
        
        stage('Login to Docker Hub') {
            steps {
                sh 'echo $DOCKER_CRED_PSW | docker login -u $DOCKER_CRED_USR --password-stdin'
                echo '✅ Connecté à Docker Hub'
            }
        }
        
        stage('Test ML Model') {
            steps {
                sh '''
                docker run --rm -v $(pwd):/app python:3.11-slim bash -c "
                    pip install numpy scikit-learn joblib
                    python /app/ml-model/train_model.py
                "
                '''
                echo '✅ Tests ML OK'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .'
                sh 'docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest'
                echo '✅ Image Docker construite'
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                sh '''
                docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                docker push ${DOCKER_IMAGE}:latest
                '''
                echo '✅ Image poussée sur Docker Hub'
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                kind load docker-image ${DOCKER_IMAGE}:${DOCKER_TAG} --name greennet
                kubectl set image deployment/energy-scaler scaler=${DOCKER_IMAGE}:${DOCKER_TAG} -n default
                kubectl rollout status deployment/energy-scaler -n default
                '''
                echo '✅ Déployé dans Kubernetes'
            }
        }
    }
    
    post {
        success {
            echo '🎉 Pipeline réussi !'
        }
        failure {
            echo '❌ Pipeline échoué'
        }
    }
}
