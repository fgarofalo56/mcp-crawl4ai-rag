# Performance Test Command

Performance testing with Playwright and Analysis Tool for comprehensive evaluation.

## Usage
```
/performance-test [--type=load|stress|spike|endurance] [--users=10] [--duration=5m]
```

## Description
Comprehensive performance testing across web interfaces, APIs, and system resources with detailed analysis and optimization recommendations.

## Implementation
1. **Test Environment Setup**: Prepare isolated testing environment
2. **Load Generation**: Generate realistic user load patterns
3. **Web Performance**: Use Playwright for web interface performance testing
4. **API Performance**: Test API endpoints under various load conditions
5. **Resource Monitoring**: Monitor system resources during tests
6. **Analysis**: Analyze results and identify bottlenecks

## Output Format
```
⚡ Performance Test Results
===========================

📊 Test Configuration:
- Test Type: {test_type}
- Virtual Users: {user_count}
- Test Duration: {duration}
- Ramp-up Time: {ramp_up}
- Environment: {test_environment}

🌐 Web Performance (Playwright):

## Page Load Metrics:
- First Contentful Paint: {fcp_average}ms (target: <1.8s)
- Largest Contentful Paint: {lcp_average}ms (target: <2.5s)
- Cumulative Layout Shift: {cls_average} (target: <0.1)
- First Input Delay: {fid_average}ms (target: <100ms)

## Core Web Vitals:
- LCP Score: {lcp_score}/100
- FID Score: {fid_score}/100
- CLS Score: {cls_score}/100
- Overall Score: {overall_score}/100

## Browser Performance:
- Chrome: {chrome_performance}
- Firefox: {firefox_performance}
- Safari: {safari_performance}
- Edge: {edge_performance}

🔌 API Performance:

## Response Time Analysis:
- Average Response Time: {avg_response_time}ms
- 95th Percentile: {p95_response_time}ms
- 99th Percentile: {p99_response_time}ms
- Max Response Time: {max_response_time}ms

## Throughput Metrics:
- Requests per Second: {rps}
- Successful Requests: {success_count} ({success_percentage}%)
- Failed Requests: {failure_count} ({failure_percentage}%)
- Error Rate: {error_rate}%

## Endpoint Performance:
{endpoint_performance_breakdown}

💾 System Resource Usage:

## CPU Utilization:
- Average CPU: {avg_cpu}%
- Peak CPU: {peak_cpu}%
- CPU Trend: {cpu_trend}

## Memory Usage:
- Average Memory: {avg_memory} GB
- Peak Memory: {peak_memory} GB
- Memory Leaks: {memory_leak_status}

## Database Performance:
- Query Response Time: {db_response_time}ms
- Connection Pool Usage: {connection_pool_usage}%
- Slow Queries: {slow_query_count}

## Azure Services Performance:
- OpenAI API Latency: {openai_latency}ms
- Storage Account I/O: {storage_iops} IOPS
- Network Latency: {network_latency}ms

📈 Load Test Results:

## {Test Type} Test Results:
- Target Load: {target_load} users
- Actual Load: {actual_load} users
- Duration: {actual_duration}
- Stability: {stability_rating}

## Performance Under Load:
- Response Time Degradation: {response_degradation}%
- Throughput Scaling: {throughput_scaling}%
- Error Rate Increase: {error_increase}%

🎯 Performance Benchmarks:

## SLA Compliance:
- Response Time SLA: {response_sla_compliance}% compliant
- Availability SLA: {availability_sla_compliance}% compliant
- Throughput SLA: {throughput_sla_compliance}% compliant

## Industry Benchmarks:
- vs. Industry Average: {industry_comparison}
- Performance Percentile: {performance_percentile}th percentile
- Optimization Potential: {optimization_potential}%

🔍 Bottleneck Analysis:

## Identified Bottlenecks:
1. {bottleneck_1}: {impact_1}
2. {bottleneck_2}: {impact_2}
3. {bottleneck_3}: {impact_3}

## Resource Constraints:
- CPU Bound Operations: {cpu_bound_operations}
- I/O Bound Operations: {io_bound_operations}
- Network Bound Operations: {network_bound_operations}

💡 Optimization Recommendations:

## High Impact Optimizations:
1. {high_impact_opt_1}
2. {high_impact_opt_2}
3. {high_impact_opt_3}

## Medium Impact Optimizations:
1. {medium_impact_opt_1}
2. {medium_impact_opt_2}

## Infrastructure Scaling:
- Recommended Scaling: {scaling_recommendation}
- Cost Impact: ${scaling_cost_impact}/month
- Performance Improvement: {performance_improvement}%

📊 Performance Comparison:
- Previous Test Score: {previous_score}/100
- Current Test Score: {current_score}/100
- Performance Trend: {performance_trend}
- Regression Issues: {regression_count}

🎯 Action Plan:
{performance_improvement_action_plan}

🔔 Monitoring Recommendations:
- Performance Alerts: {performance_alert_setup}
- Continuous Monitoring: {continuous_monitoring_setup}
- Automated Testing: {automated_testing_schedule}
```

## Test Types
- `--type=load`: Standard load testing (default)
- `--type=stress`: Stress testing to find breaking points
- `--type=spike`: Sudden load spike testing
- `--type=endurance`: Long-duration endurance testing

## Parameters
- `--users=10`: Number of virtual users (default: 10)
- `--duration=5m`: Test duration (default: 5 minutes)

## Performance Metrics
- **Web Vitals**: Core Web Vitals for user experience
- **API Performance**: Response times, throughput, error rates
- **System Resources**: CPU, memory, database performance
- **Network Performance**: Latency, bandwidth utilization
- **Azure Services**: Cloud service performance metrics

## MCP Servers Used
- **Playwright MCP**: Web performance testing and Core Web Vitals measurement
- **Analysis Tool**: Performance metrics calculation and bottleneck analysis
- **Azure-mcp MCP**: Azure service performance monitoring
- **AI-Server-Sequential-thinking**: Performance analysis and optimization reasoning
