pipeline {
    agent any   

    environment {
        // Global environment variables
        APP_NAME = 'my-flask-app'
        DEPLOY_ENV = '10.10.128.2'
        SSH_CREDS = ''
        DOCKER_IMAGE = 'shaikhs9/my-flask-app'  // Change to your Docker Hub image name
        DOCKER_CREDENTIALS = credentials('docker-username-pass') 
        GIT_BRANCH = 'main'
    }

    stages {
        // Checkout the source code from SCM (e.g., GitHub)
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        // Run Tests
        stage('Run Tests') {
            agent {
                docker {
                    image 'python:3.8' // Use Python 3.8 Docker image
                }
            }
            steps {
                script {
                    def result = sh(script: '''
                        # Create a Python virtual environment
                        python -m venv venv

                        # Activate the virtual environment
                        source venv/bin/activate

                        # Upgrade pip to the latest version
                        pip install --upgrade pip

                        # Install required packages from requirements.txt
                        pip install -r requirements.txt

                        # Run tests and capture the exit code
                        pytest test.py --maxfail=5 --disable-warnings --tb=short
                        exit_code=$?

                        # Deactivate the virtual environment
                        deactivate

                        # Exit with the test result code
                        exit $exit_code
                    ''', returnStatus: true)

                    if (result != 0) {
                        currentBuild.result = 'FAILURE'
                        error("Test cases failed. Stopping pipeline.")
                    }
                }

        // Build Docker image
        stage('Build Docker Image') {
            when {
                branch 'main' // Only deploy from the main branch
            }
            steps {
                script {
                    // Build the Docker image
                    sh "docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} ."
                }
            }
        }

        // Push Docker image to Docker Hub
        stage('Push to Docker Hub') {
            steps {
                script {
                    // Log in to Docker Hub using Docker Hub username and PAT
                    withCredentials([usernamePassword(credentialsId: 'docker-username-pass', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        // Log in to Docker using the username (Docker Hub) and PAT (Personal Access Token)
                        sh "echo \$DOCKER_PASSWORD | docker login -u \$DOCKER_USERNAME --password-stdin"
                    }

                    // Push the image to Docker Hub
                    sh "docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                }
            }
        }

        // SSH and Deploy to Staging Environment
        stage('SSH and Deploy to Staging Environment') {
            steps {
                script {
                    // Load SSH private key from Jenkins credentials and deploy to server
                    sshagent(['trex-jenkins']) {
                        sh '''#!/bin/bash
                        # Docker login on staging server
                        ssh -o StrictHostKeyChecking=no trex@${DEPLOY_ENV} "echo \$DOCKER_PASSWORD | docker login -u \$DOCKER_USERNAME --password-stdin"
                        
                        # Pull the Docker image for the specific build number
                        ssh -o StrictHostKeyChecking=no trex@${DEPLOY_ENV} "docker pull ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                        
                        # Run the Docker container
                        ssh -o StrictHostKeyChecking=no trex@${DEPLOY_ENV} "docker run -d ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                        
                        # Remove old Docker images if BUILD_NUMBER > 2
                        BUILD_NUMBER_MINUS_TWO=\$((BUILD_NUMBER - 2))
                        if [ \${BUILD_NUMBER} -gt 2 ]; then
                            ssh -o StrictHostKeyChecking=no trex@${DEPLOY_ENV} "docker rmi ${DOCKER_IMAGE}:\${BUILD_NUMBER_MINUS_TWO}"
                        fi
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Tests passed and deployment to staging was successful.'
        }
        failure {
            echo 'Tests failed or deployment to staging failed.'
        }
        always {
            // Clean up Docker images after the build
            sh "docker rmi ${DOCKER_IMAGE}:${BUILD_NUMBER} || true"
            sh "rm -rf ./"
        }
    }
}
