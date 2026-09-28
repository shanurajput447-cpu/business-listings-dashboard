import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import {
  getCityCounts,
  getCategoryCounts,
  getSourceCounts,
} from "../services/apiClient";

const CITY_BAR_COLOR = "#4f46e5";
const CATEGORY_BAR_COLOR = "#4338ca";
const SOURCE_COLORS = ["#1e3a8a", "#3730a3", "#4f46e5", "#818cf8"];
const GRID_STROKE = "#e8eef5";
const TICK_STYLE = { fill: "#64748b", fontSize: 12 };

function IconBuilding() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        d="M4 21V5.5A1.5 1.5 0 0 1 5.5 4h5A1.5 1.5 0 0 1 12 5.5V8h6.5A1.5 1.5 0 0 1 20 9.5V21h-5v-5h-6v5H4Zm2-2h2v-3h8v3h2V10h-6V6H6v13Zm2-6V9h2v4H8Zm0-6V5h2v2H8Zm4 6v-2h2v2h-2Zm0-4V9h2v2h-2Zm4 4v-2h2v2h-2Z"
      />
    </svg>
  );
}

function IconPin() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        d="M12 22s7-7.1 7-12a7 7 0 1 0-14 0c0 4.9 7 12 7 12Zm0-9.5A2.5 2.5 0 1 1 12 8a2.5 2.5 0 0 1 0 4.5Z"
      />
    </svg>
  );
}

function IconTag() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        d="M21 12.2 12.2 3.4A2 2 0 0 0 10.8 3H5a2 2 0 0 0-2 2v5.8a2 2 0 0 0 .6 1.4L12.4 21a2 2 0 0 0 2.8 0l5.8-5.8a2 2 0 0 0 0-2.8ZM7.25 8.5A1.25 1.25 0 1 1 8.5 7.25 1.25 1.25 0 0 1 7.25 8.5Z"
      />
    </svg>
  );
}

function IconGlobe() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2Zm7.9 9h-3.2a15.4 15.4 0 0 0-1.4-5.3A8.05 8.05 0 0 1 19.9 11ZM12 20a13.6 13.6 0 0 1-2.3-7h4.6A13.6 13.6 0 0 1 12 20ZM9.7 11A13.6 13.6 0 0 1 12 4a13.6 13.6 0 0 1 2.3 7H9.7ZM8.7 5.7A15.4 15.4 0 0 0 7.3 11H4.1A8.05 8.05 0 0 1 8.7 5.7ZM4.1 13h3.2a15.4 15.4 0 0 0 1.4 5.3A8.05 8.05 0 0 1 4.1 13Zm11.2 5.3a15.4 15.4 0 0 0 1.4-5.3h3.2a8.05 8.05 0 0 1-4.6 5.3Z"
      />
    </svg>
  );
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) {
    return null;
  }

  const item = payload[0];
  const title = label || item.name || item.payload?.source || "";

  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label">{title}</p>
      <p className="chart-tooltip-value">{item.value} listings</p>
    </div>
  );
}

function getHighestCategories(categoryData) {
  if (!categoryData.length) {
    return { label: "—", count: 0 };
  }

  const maxCount = Math.max(
    ...categoryData.map((item) => Number(item.count || 0))
  );
  const names = categoryData
    .filter((item) => Number(item.count || 0) === maxCount)
    .map((item) => item.category);

  return {
    label: names.join(", "),
    count: maxCount,
  };
}

function Dashboard() {
  const [cityData, setCityData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [sourceData, setSourceData] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError("");

        const [cities, categories, sources] = await Promise.all([
          getCityCounts(),
          getCategoryCounts(),
          getSourceCounts(),
        ]);

        setCityData(cities);
        setCategoryData(categories);
        setSourceData(sources);
      } catch (err) {
        console.error("Dashboard API error:", err);
        setError(
          "Unable to load dashboard data. Please make sure the FastAPI backend is running."
        );
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const totalBusinesses = cityData.reduce(
    (total, item) => total + Number(item.count || 0),
    0
  );

  const totalCities = cityData.length;
  const totalCategories = categoryData.length;
  const totalSources = sourceData.length;
  const averagePerCity = totalCities
    ? Number((totalBusinesses / totalCities).toFixed(1)).toString().replace(
        /\.0$/,
        ""
      )
    : "0";
  const highestCategory = getHighestCategories(categoryData);

  if (loading) {
    return (
      <main className="dashboard-page">
        <div className="dashboard-container">
          <div className="status-card">Loading dashboard data...</div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="dashboard-page">
        <div className="dashboard-container">
          <div className="error-card">{error}</div>
        </div>
      </main>
    );
  }

  return (
    <main className="dashboard-page">
      <div className="dashboard-container">
        <header className="dashboard-header">
          <div>
            <p className="eyebrow">BUSINESS INTELLIGENCE</p>
            <h1>Business Listings Dashboard</h1>
            <p className="subtitle">
              Explore business coverage across cities, categories, and data
              sources.
            </p>
          </div>

          <div className="live-badge">
            <span className="live-dot"></span>
            Live Data
          </div>
        </header>

        <section className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-icon kpi-icon-business">
              <IconBuilding />
            </div>
            <div className="kpi-copy">
              <span>Total Businesses</span>
              <strong>{totalBusinesses}</strong>
            </div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon kpi-icon-cities">
              <IconPin />
            </div>
            <div className="kpi-copy">
              <span>Total Cities</span>
              <strong>{totalCities}</strong>
            </div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon kpi-icon-categories">
              <IconTag />
            </div>
            <div className="kpi-copy">
              <span>Total Categories</span>
              <strong>{totalCategories}</strong>
            </div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon kpi-icon-sources">
              <IconGlobe />
            </div>
            <div className="kpi-copy">
              <span>Total Sources</span>
              <strong>{totalSources}</strong>
            </div>
          </div>
        </section>

        <section className="charts-grid">
          <div className="chart-card chart-card-wide">
            <div className="chart-header">
              <div>
                <h2>Businesses by City</h2>
                <p>Number of listings across cities</p>
              </div>
            </div>

            <div className="chart-container">
              <ResponsiveContainer width="100%" height={350}>
                <BarChart
                  data={cityData}
                  margin={{ top: 12, right: 12, left: 0, bottom: 56 }}
                >
                  <CartesianGrid
                    stroke={GRID_STROKE}
                    strokeDasharray="3 3"
                    vertical={false}
                  />
                  <XAxis
                    dataKey="city"
                    angle={-35}
                    textAnchor="end"
                    interval={0}
                    height={72}
                    tick={TICK_STYLE}
                    axisLine={{ stroke: "#dbe3ee" }}
                    tickLine={false}
                  />
                  <YAxis
                    allowDecimals={false}
                    tick={TICK_STYLE}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    cursor={{ fill: "rgba(79, 70, 229, 0.06)" }}
                    content={<ChartTooltip />}
                  />
                  <Bar
                    dataKey="count"
                    name="Businesses"
                    fill={CITY_BAR_COLOR}
                    radius={[6, 6, 0, 0]}
                    maxBarSize={42}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card chart-card-wide">
            <div className="chart-header">
              <div>
                <h2>Businesses by Category</h2>
                <p>Distribution across business categories</p>
              </div>
            </div>

            <div className="chart-container">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart
                  data={categoryData}
                  layout="vertical"
                  margin={{ top: 8, right: 24, left: 8, bottom: 8 }}
                >
                  <CartesianGrid
                    stroke={GRID_STROKE}
                    strokeDasharray="3 3"
                    horizontal={false}
                  />
                  <XAxis
                    type="number"
                    allowDecimals={false}
                    tick={TICK_STYLE}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    type="category"
                    dataKey="category"
                    width={128}
                    tick={TICK_STYLE}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    cursor={{ fill: "rgba(67, 56, 202, 0.06)" }}
                    content={<ChartTooltip />}
                  />
                  <Bar
                    dataKey="count"
                    name="Businesses"
                    fill={CATEGORY_BAR_COLOR}
                    radius={[0, 6, 6, 0]}
                    maxBarSize={18}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card">
            <div className="chart-header">
              <div>
                <h2>Businesses by Source</h2>
                <p>Listings grouped by source</p>
              </div>
            </div>

            <div className="chart-container pie-container">
              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <Pie
                    data={sourceData}
                    dataKey="count"
                    nameKey="source"
                    cx="50%"
                    cy="46%"
                    innerRadius={68}
                    outerRadius={108}
                    paddingAngle={3}
                    stroke="#ffffff"
                    strokeWidth={2}
                    label={({ percent }) => `${Math.round(percent * 100)}%`}
                    labelLine={false}
                  >
                    {sourceData.map((entry, index) => (
                      <Cell
                        key={`source-${entry.source}-${index}`}
                        fill={SOURCE_COLORS[index % SOURCE_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip content={<ChartTooltip />} />
                  <Legend
                    verticalAlign="bottom"
                    iconType="circle"
                    wrapperStyle={{ fontSize: 12, color: "#475569" }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card summary-card">
            <div className="chart-header">
              <div>
                <h2>Quick Insights</h2>
                <p>Calculated from live API aggregations</p>
              </div>
            </div>

            <div className="summary-list">
              <div className="summary-row">
                <span>Total listings</span>
                <strong>{totalBusinesses}</strong>
              </div>

              <div className="summary-row">
                <span>Cities covered</span>
                <strong>{totalCities}</strong>
              </div>

              <div className="summary-row">
                <span>Categories</span>
                <strong>{totalCategories}</strong>
              </div>

              <div className="summary-row">
                <span>Sources</span>
                <strong>{totalSources}</strong>
              </div>

              <div className="summary-row">
                <span>Average listings / city</span>
                <strong>{averagePerCity}</strong>
              </div>

              <div className="summary-row summary-row-highlight">
                <span>Highest category</span>
                <strong>
                  {highestCategory.label}
                  <em>
                    {highestCategory.count
                      ? ` · ${highestCategory.count} listings`
                      : ""}
                  </em>
                </strong>
              </div>
            </div>
          </div>
        </section>

        <footer className="dashboard-footer">
          Data is fetched from FastAPI and aggregated from MySQL.
        </footer>
      </div>
    </main>
  );
}

export default Dashboard;
