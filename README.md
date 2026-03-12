# Garuda Analytics Dashboard

A full-stack analytics dashboard built with React, Flask, PostgreSQL, and Machine Learning. This application allows users to upload CSV datasets, analyze data, and run machine learning predictions with interactive visualizations.

## 🚀 Features

- **User Authentication**: JWT-based secure authentication system
- **Data Upload**: CSV file upload with data validation and preview
- **Data Analysis**: Automatic data profiling and statistics
- **Machine Learning**: Linear Regression predictions with scikit-learn
- **Interactive Charts**: Data visualization using Recharts
- **Responsive Design**: Modern UI with Tailwind CSS
- **REST API**: Well-structured API endpoints
- **Database Integration**: PostgreSQL for data persistence

## 🛠 Tech Stack

### Frontend
- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and development server
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Recharts** - Data visualization library
- **Lucide React** - Icon library

### Backend
- **Flask** - Python web framework
- **PostgreSQL** - Relational database
- **psycopg2** - PostgreSQL adapter
- **JWT** - Authentication tokens
- **scikit-learn** - Machine learning library
- **pandas** - Data processing
- **Flask-CORS** - Cross-origin resource sharing

## 📁 Project Structure

```
Garuda_dashboard/
│
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection and operations
│   ├── model.py               # Data models
│   ├── auth.py                # Authentication utilities
│   ├── routes/
│   │   ├── login.py           # Authentication routes
│   │   ├── upload.py          # File upload routes
│   │   └── predict.py         # ML prediction routes
│   └── requirements.txt       # Python dependencies
│
├── frontend/
│   ├── index.html            # HTML template
│   ├── package.json          # Node.js dependencies
│   ├── vite.config.js        # Vite configuration
│   └── src/
│       ├── main.jsx          # Application entry point
│       ├── App.jsx           # Main app component
│       ├── index.css         # Global styles
│       ├── api/
│       │   └── api.js        # API service layer
│       ├── contexts/
│       │   └── AuthContext.jsx # Authentication context
│       ├── pages/
│       │   ├── Login.jsx     # Login page
│       │   ├── Dashboard.jsx # Analytics dashboard
│       │   └── Upload.jsx    # File upload page
│       └── components/
│           ├── Layout.jsx    # Layout component
│           └── Chart.jsx     # Chart visualization component
│
└── README.md                 # This file
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **PostgreSQL** (v12 or higher)
- **Git**

### Database Setup

1. **Install PostgreSQL** if not already installed
2. **Create a database**:
   ```sql
   CREATE DATABASE garuda_analytics;
   ```
3. **Create a user** (optional):
   ```sql
   CREATE USER garuda_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE garuda_analytics TO garuda_user;
   ```

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional):
   ```bash
   # Windows
   set DB_HOST=localhost
   set DB_NAME=garuda_analytics
   set DB_USER=postgres
   set DB_PASSWORD=your_password
   
   # macOS/Linux
   export DB_HOST=localhost
   export DB_NAME=garuda_analytics
   export DB_USER=postgres
   export DB_PASSWORD=your_password
   ```

5. **Start the backend server**:
   ```bash
   python app.py
   ```

   The backend will be available at: `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

   The frontend will be available at: `http://localhost:3000`

## 📖 Usage

### 1. Login

- Open the application in your browser
- Use demo credentials:
  - **Username**: `admin`
  - **Password**: `admin123`
- Additional demo users: `user/user123`, `demo/demo123`

### 2. Upload Data

- Navigate to the "Upload Data" page
- Drag and drop a CSV file or click to select
- Supported format: CSV files with headers
- Maximum file size: 16MB

### 3. Analyze Data

- On the Dashboard, view data statistics
- See column information and data types
- Check for missing values

### 4. Run Predictions

- Select a target column (what you want to predict)
- Choose feature columns (input variables)
- Click "Run Prediction" to train the model
- View results with interactive charts

## 🔌 API Endpoints

### Authentication

- `POST /login` - User login and token generation
- `POST /auth/verify` - Token verification
- `POST /auth/logout` - User logout

### Data Management

- `POST /api/upload` - Upload CSV file
- `GET /api/data-info` - Get uploaded data information
- `DELETE /api/clear-data` - Clear uploaded data

### Machine Learning

- `POST /api/predict` - Run ML prediction
- `GET /api/prediction-results` - Get prediction results
- `GET /api/model-info` - Get model information

### Health Check

- `GET /health` - API health status

### Example API Requests

#### Login
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

#### Upload CSV
```bash
curl -X POST http://localhost:5000/api/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@your_data.csv"
```

#### Run Prediction
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_column": "target",
    "feature_columns": ["feature1", "feature2"],
    "model_type": "LinearRegression"
  }'
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🔧 Configuration

### Backend Configuration

Edit `backend/config.py` to modify:

- Database connection settings
- JWT secret key
- CORS origins
- File upload limits

### Frontend Configuration

Edit `frontend/src/api/api.js` to modify:

- API base URL
- Request timeout
- Error handling

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check database credentials in config.py
   - Verify database exists

2. **CORS Errors**
   - Ensure backend server is running
   - Check CORS configuration in config.py

3. **JWT Token Issues**
   - Clear browser localStorage
   - Check token expiration
   - Verify secret key consistency

4. **File Upload Issues**
   - Check file format (CSV only)
   - Verify file size (< 16MB)
   - Ensure CSV has headers

### Debug Mode

Enable debug mode by setting:
```bash
export FLASK_ENV=development
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- React team for the excellent framework
- Flask community for the robust web framework
- scikit-learn team for the ML library
- Recharts team for the visualization library

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review the API documentation

---

**Happy Analyzing! 🦅**
