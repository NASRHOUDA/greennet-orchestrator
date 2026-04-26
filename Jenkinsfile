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
  - name: docker
    image: docker:24-dind
    command: ["sleep", "infinity"]
    securityContext:
      privileged: true
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
    - name: DOCKER_HOST
      value: "unix:///var/run/docker.sock"
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["sleep", "infinity"]
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
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
                container('docker') {
                    sh '''
                    sleep 5
                    docker info
                    echo $DOCKER_CRED_PSW | docker login -u $DOCKER_CRED_USR --password-stdin
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                    docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker push ${DOCKER_IMAGE}:latest
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
