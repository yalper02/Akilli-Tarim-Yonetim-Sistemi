export interface Farm {
  id: number
  name: string
  location: string
}

export interface Me {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface SensorReading {
  id: number
  device: number
  device_name?: string
  capability_type: string
  value: number
  time: string
}

export interface Command {
  id: number
  device: number
  device_name?: string
  action_type: string
  status: 'pending' | 'sent' | 'received' | 'executed' | 'failed'
  triggered_by: 'rule' | 'manual'
  created_at: string
}

export interface Notification {
  id: number
  farm: number | null
  title: string
  message: string
  notification_type: string
  severity: 'info' | 'warning' | 'critical'
  is_read: boolean
  related_object_type: string | null
  related_object_id: number | null
  created_at: string
}

export interface DeviceCapability {
  id: number
  capability_type: string
  unit: string
  min_value: number | null
  max_value: number | null
}

export interface Device {
  id: number
  farm: number
  name: string
  device_uid: string
  device_type: 'sensor' | 'actuator' | 'combined'
  status: 'online' | 'offline'
  status_display: string
  location_description: string
  installed_at: string | null
  last_seen_at: string | null
  mqtt_username: string
  capabilities: DeviceCapability[]
}

export interface DeviceHealth {
  device_id: number
  status: string
  last_seen_at: string | null
  battery_level: number | null
  rssi: number | null
}

export interface RuleCondition {
  id: number
  capability_type: string
  operator: string
  threshold_value: number
}

export interface RuleAction {
  id: number
  action_type: string
  device: number
  parameters: Record<string, unknown>
  priority: number
}

export interface RuleWeatherConstraint {
  id: number
  max_rain_probability_pct: number
  check_hours_ahead: number
}

export interface Rule {
  id: number
  farm: number
  name: string
  description: string
  is_active: boolean
  created_by: number
  created_by_username: string
  created_at: string
  updated_at: string
  conditions: RuleCondition[]
  actions: RuleAction[]
  weather_constraint: RuleWeatherConstraint | null
}

export interface Prediction {
  id: number
  prediction_type: string
  value: number
  confidence: number
  created_at: string
}

export interface TimeseriesPoint {
  bucket: string
  avg_value: number
  min_value: number
  max_value: number
}
