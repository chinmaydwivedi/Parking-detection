# Parking Detection System

## Concept

The Parking Detection System is an application that uses computer vision techniques to detect and monitor parking spaces in real-time. The system analyzes video feeds from parking areas to determine which spots are occupied and which are available. This information can be used for:

- Real-time parking availability monitoring
- Parking usage analytics
- Smart parking management
- Automated parking guidance systems

The detection is based on image processing and machine learning algorithms that can identify vehicles in designated parking spaces and track changes in their occupancy status.

## Requirements

- Python 3.6+
- OpenCV
- NumPy
- TensorFlow or PyTorch (depending on the implementation)
- CUDA toolkit (optional, for GPU acceleration)
- Webcam or video input source

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Parking-detection.git
cd Parking-detection
```

### 2. Set Up Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the System

### 1. Configure Input Source

Edit the configuration file `config.json` to specify your video input source:

```json
{
    "input_source": "camera",  // Options: "camera", "video_file", "rtsp"
    "camera_id": 0,            // Camera device ID (if using camera)
    "video_path": "videos/parking_lot.mp4",  // Path to video file (if using video_file)
    "rtsp_url": "rtsp://example.com/stream"  // RTSP URL (if using rtsp)
}
```

### 2. Define Parking Spaces

Run the setup utility to define parking spaces:

```bash
python setup_parking_spaces.py
```

Follow the on-screen instructions to:
- Select points to define each parking space
- Save the parking space coordinates

### 3. Start the Detection System

```bash
python detect_parking.py
```

The system will:
1. Initialize the video input source
2. Load the defined parking spaces
3. Process each frame to detect parked vehicles
4. Display results in real-time with occupied/available status for each space

### 4. View Analytics (Optional)

To view parking usage analytics:

```bash
python generate_analytics.py
```

This will produce reports and visualizations of parking space usage over time.

## Troubleshooting

- **Error: Cannot open camera/video file**: Verify your input source configuration
- **Poor detection accuracy**: Try adjusting the detection parameters in `config.json`
- **Performance issues**: Consider enabling GPU acceleration or reducing input resolution

## Contributing

Contributions to improve the system are welcome. Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
