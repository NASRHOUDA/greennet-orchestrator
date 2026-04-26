pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: docker
    image: docker:24-dind
    securityContext:
      privileged: true
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["sleep", "infinity"]
  - name: python
    image: python:3.11-slim
    command: ["sleep", "infinity"]
'''
            defaultContainer 'docker'
        }
    }

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

        stage('Test ML Model') {
            steps {
                container('python') {
                    sh '''
                    pip install numpy scikit-learn joblib -q
                    python ml-model/train_model.py
                    '''
                }
                echo '✅ Tests ML OK'
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                container('docker') {
                    sh '''
                    echo $DOCKER_CRED_PSW | docker login -u $DOCKER_CRED_USR --password-stdin
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                    docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker push ${DOCKER_IMAGE}:latest
                    '''
                }
                echo '✅ Image construite et poussée'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    sh '''
                    kubectl set image deployment/energy-scaler scaler=${DOCKER_IMAGE}:${DOCKER_TAG} -n default
                    kubectl rollout status deployment/energy-scaler -n default
                    '''
                }
                echo '✅ Déployé'
            }
        }
    }

    post {
        success { echo '🎉 Pipeline réussi !' }
        failure { echo '❌ Pipeline échoué' }
    }
}
