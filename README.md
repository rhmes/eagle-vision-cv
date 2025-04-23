# Eagle Vision CV
Eagle Vision CV is a computer vision project designed to process and analyze offline recorded data using the YOLO detector and DeepSORT tracker. It leverages MongoDB and PostgreSQL databases, all running within a microservices architecture to ensure scalability and modularity.

## Features
- Advanced image processing.
- Object detection and recognition.
- Real-time video analysis.

## Prerequisites
- Docker and Docker Compose installed on your system.

**Important Note:** Ensure that the recording to be processed is placed in the `app/recordings` directory. Additionally, update the file path in `app/api/routes.py` to reflect the correct location of the recording.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/eagle-vision-cv.git
    cd eagle-vision-cv
    ```
2. Build and start the application using Docker Compose:
    ```bash
    docker-compose up --build
    ```

## Running Commands
- To run the application:
  ```bash
  docker-compose up
  ```
- To stop the application:
  ```bash
  docker-compose down
  ```
- To run tests:
  ```bash
  docker-compose run app python -m unittest discover tests
  ```

## Results
Access the results on your browser at: [http://0.0.0.0:8000/video-ui/](http://0.0.0.0:8000/video-ui/)

