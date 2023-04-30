# PDFInsight

This repository contains the PDFInsight project, which is a tool for analyzing PDF files and detecting potentially malicious content. The application is built using Python and comes with a Docker configuration for easy deployment and usage.

## Prerequisites

To run this project, you need to have [Docker](https://www.docker.com/products/docker-desktop) installed on your system.

## Getting Started

1. Clone this repository

2. Build the Docker image:

```
docker build -t pdfanalyzer:1.0 .
```

3. Run the Docker container:

```
docker run -it -p 8050:8050 -v /path/to/your/input/directory:/input --name pdfanalyzer_instance pdfanalyzer:1.0 /bin/bash
```

Make sure to replace `/path/to/your/input/directory` with the absolute path to the directory containing your PDF files.

4. Inside the Docker container, run the `entry_script.py`:

```
python entry_script.py
```

5. Access the PDF Analyzer Dashboard in your web browser:

Open your web browser and navigate to [http://localhost:8050](http://localhost:8050) or [http://0.0.0.0:8050](http://0.0.0.0:8050).

6. Stop the Docker container:

When you're done using the application, you can exit the Docker container by typing `exit` in the container's terminal.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
