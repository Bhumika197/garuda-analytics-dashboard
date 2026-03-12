import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter
} from 'recharts'

/**
 * Chart Component
 * Displays prediction results using Recharts
 */
function Chart({ data, targetColumn }) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No data available for visualization
      </div>
    )
  }

  // Prepare data for charts
  const chartData = data.map((item, index) => ({
    index: index + 1,
    actual: item.actual,
    predicted: item.predicted,
    residual: item.residual
  }))

  // Custom tooltip for better formatting
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-md shadow-lg">
          <p className="text-sm font-medium text-gray-900">Row {label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(4) : entry.value}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-8">
      {/* Actual vs Predicted Line Chart */}
      <div>
        <h4 className="text-md font-medium text-gray-900 mb-4">
          Actual vs Predicted Values
        </h4>
        <div className="bg-gray-50 p-4 rounded-lg">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis 
                dataKey="index" 
                label={{ value: 'Data Point', position: 'insideBottom', offset: -5 }}
                stroke="#666"
              />
              <YAxis 
                label={{ value: targetColumn || 'Value', angle: -90, position: 'insideLeft' }}
                stroke="#666"
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="actual" 
                stroke="#2563eb" 
                strokeWidth={2}
                dot={false}
                name="Actual"
              />
              <Line 
                type="monotone" 
                dataKey="predicted" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={false}
                name="Predicted"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Scatter Plot: Actual vs Predicted */}
      <div>
        <h4 className="text-md font-medium text-gray-900 mb-4">
          Actual vs Predicted Scatter Plot
        </h4>
        <div className="bg-gray-50 p-4 rounded-lg">
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis 
                type="number" 
                dataKey="actual" 
                name="Actual"
                label={{ value: 'Actual Values', position: 'insideBottom', offset: -5 }}
                stroke="#666"
              />
              <YAxis 
                type="number" 
                dataKey="predicted" 
                name="Predicted"
                label={{ value: 'Predicted Values', angle: -90, position: 'insideLeft' }}
                stroke="#666"
              />
              <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
              <Scatter 
                name="Predictions" 
                data={chartData} 
                fill="#2563eb"
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Points closer to the diagonal line indicate better predictions
        </p>
      </div>

      {/* Residuals Chart */}
      <div>
        <h4 className="text-md font-medium text-gray-900 mb-4">
          Prediction Residuals (Actual - Predicted)
        </h4>
        <div className="bg-gray-50 p-4 rounded-lg">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis 
                dataKey="index" 
                label={{ value: 'Data Point', position: 'insideBottom', offset: -5 }}
                stroke="#666"
              />
              <YAxis 
                label={{ value: 'Residual', angle: -90, position: 'insideLeft' }}
                stroke="#666"
              />
              <Tooltip content={<CustomTooltip />} />
              <Line 
                type="monotone" 
                dataKey="residual" 
                stroke="#f59e0b" 
                strokeWidth={2}
                dot={false}
                name="Residual"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Residuals should be randomly distributed around zero for a good model
        </p>
      </div>

      {/* Statistics Summary */}
      <div>
        <h4 className="text-md font-medium text-gray-900 mb-4">
          Prediction Statistics
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Mean Actual</p>
            <p className="text-lg font-bold text-gray-900">
              {(chartData.reduce((sum, item) => sum + item.actual, 0) / chartData.length).toFixed(4)}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Mean Predicted</p>
            <p className="text-lg font-bold text-gray-900">
              {(chartData.reduce((sum, item) => sum + item.predicted, 0) / chartData.length).toFixed(4)}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Mean Absolute Residual</p>
            <p className="text-lg font-bold text-gray-900">
              {(chartData.reduce((sum, item) => sum + Math.abs(item.residual), 0) / chartData.length).toFixed(4)}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Chart
