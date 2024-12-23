pipeline {
    agent any   

    environment {
        // Global environment variables
        APP_NAME = 'my-flask-app'
        DEPLOY_ENV = '10.10.128.2'
        SSH_CREDS = ''  // Add your SSH credentials here
        DOCKER_IMAGE = 'shaikhs9/my-flask-app'  // Change to your Docker Hub image name
        DOCKER_CREDENTIALS = credentials('docker-username-pass')  // Docker credentials stored in Jenkins
        GIT_BRANCH = 'main'  // Branch to deploy from
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
            steps {
                script {
                    // Running tests and stopping the pipeline if tests fail
                    def result = sh(script: 'pytest test.py --maxfail=5 --disable-warnings --tb=short', returnStatus: true)
                    if (result != 0) {
                        currentBuild.result = 'FAILURE'
                        error("Test cases failed. Stopping pipeline.")
                    }
                }
            }
        }

        // Build Docker Image
        stage('Build Docker Image') {
            when {
                branch 'main'  // Only build and deploy from the main branch
            }
            steps {
                script {
                    // Build Docker image with the tag as BUILD_NUMBER
                    sh "docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} ."
                }
            }
        }

        // Push Docker Image to Docker Hub
        stage('Push to Docker Hub') {
            steps {
                script {
                    // Log in to Docker Hub using Jenkins credentials
                    withCredentials([usernamePassword(credentialsId: 'docker-username-pass', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        // Log in to Docker Hub using the credentials
                        sh "echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin"
                    }

                    // Push the built Docker image to Docker Hub
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


    post {
        success {
            // On successful build and deployment
            echo 'Tests passed and deployment to staging was successful.'
        }
        failure {
            // On failure in tests or deployment
            echo 'Tests failed or deployment to staging failed.'
        }
        always {
            // Clean up Docker images after the build
            sh "docker rmi ${DOCKER_IMAGE}:${BUILD_NUMBER} || true"
            sh "rm -rf ./"
        }
    }
}
