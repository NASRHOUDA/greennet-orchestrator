pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'energy-scaler'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo '✅ Code récupéré'
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
        
        stage('Security Scan') {
            steps {
                sh '''
                docker run --rm aquasec/trivy image --severity HIGH,CRITICAL --exit-code 0 python:3.11-slim
                '''
                echo '✅ Scan sécurité terminé'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .'
                sh 'docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest'
                echo '✅ Image Docker construite'
            }
        }
        
        stage('Deploy to Kind') {
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
