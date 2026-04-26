pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:latest
  - name: python
    image: python:3.11-slim
    command: ["sleep", "infinity"]
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command: ["sleep", "infinity"]
    env:
    - name: container
      value: docker
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["sleep", "infinity"]
'''
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
                    pip install -r ml-model/requirements.txt -q
                    python ml-model/train_model.py
                    echo "✅ Tests ML OK"
                    '''
                }
            }
        }
        stage('Build & Push Docker Image') {
            steps {
                container('kaniko') {
                    sh '''
                    mkdir -p /kaniko/.docker
                    echo "{\\"auths\\":{\\"https://index.docker.io/v1/\\":{\\"auth\\":\\"$(echo -n $DOCKER_CRED_USR:$DOCKER_CRED_PSW | base64)\\"}}}" > /kaniko/.docker/config.json
                    /kaniko/executor \
                      --context=$(pwd) \
                      --dockerfile=$(pwd)/Dockerfile \
                      --destination=${DOCKER_IMAGE}:${DOCKER_TAG} \
                      --destination=${DOCKER_IMAGE}:latest
                    echo "✅ Image poussée sur Docker Hub"
                    '''
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        sh '''
                        kubectl set image deployment/energy-scaler \
                          scaler=${DOCKER_IMAGE}:${DOCKER_TAG} -n default
                        kubectl rollout status deployment/energy-scaler -n default
                        echo "✅ Déployé dans Kubernetes"
                        '''
                    }
                }
            }
        }
    }
    post {
        success { echo '🎉 Pipeline réussi !' }
        failure { echo '❌ Pipeline échoué' }
    }
}
