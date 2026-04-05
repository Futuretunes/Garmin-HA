"""Constants for Garmin HA integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength,
    UnitOfTime,
    UnitOfTemperature,
)

DOMAIN = "garmin_ha"
DEFAULT_UPDATE_INTERVAL = 300  # 5 minutes
WEBHOOK_ID_PREFIX = "garmin_ha_"

CONF_WEBHOOK_ID = "webhook_id"


@dataclass(frozen=True, kw_only=True)
class GarminSensorEntityDescription(SensorEntityDescription):
    """Describes a Garmin sensor."""

    value_key: str
    source: str = "daily_summary"


DAILY_SUMMARY_SENSORS: tuple[GarminSensorEntityDescription, ...] = (
    GarminSensorEntityDescription(
        key="total_steps",
        translation_key="total_steps",
        name="Total Steps",
        icon="mdi:walk",
        native_unit_of_measurement="steps",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="totalSteps",
        source="daily_summary",
    ),
    GarminSensorEntityDescription(
        key="daily_step_goal",
        translation_key="daily_step_goal",
        name="Daily Step Goal",
        icon="mdi:flag-checkered",
        native_unit_of_measurement="steps",
        value_key="dailyStepGoal",
        source="daily_summary",
    ),
    GarminSensorEntityDescription(
        key="total_distance",
        translation_key="total_distance",
        name="Total Distance",
        icon="mdi:map-marker-distance",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.METERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="totalDistanceMeters",
        source="daily_summary",
    ),
    GarminSensorEntityDescription(
        key="active_calories",
        translation_key="active_calories",
        name="Active Calories",
        icon="mdi:fire",
        native_unit_of_measurement="kcal",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="activeKilocalories",
        source="daily_summary",
    ),
    GarminSensorEntityDescription(
        key="total_calories",
        translation_key="total_calories",
        name="Total Calories",
        icon="mdi:fire",
        native_unit_of_measurement="kcal",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="totalKilocalories",
        source="daily_summary",
    ),
    GarminSensorEntityDescription(
        key="floors_ascended",
        translation_key="floors_ascended",
        name="Floors Ascended",
        icon="mdi:stairs-up",
        native_unit_of_measurement="floors",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="floorsAscended",
        source="daily_summary",
    ),
    GarminSensorEntityDescription(
        key="floors_descended",
        translation_key="floors_descended",
        name="Floors Descended",
        icon="mdi:stairs-down",
        native_unit_of_measurement="floors",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="floorsDescended",
        source="daily_summary",
    ),
    GarminSensorEntityDescription(
        key="moderate_intensity_minutes",
        translation_key="moderate_intensity_minutes",
        name="Moderate Intensity Minutes",
        icon="mdi:speedometer-medium",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="moderateIntensityMinutes",
        source="daily_summary",
    ),
    GarminSensorEntityDescription(
        key="vigorous_intensity_minutes",
        translation_key="vigorous_intensity_minutes",
        name="Vigorous Intensity Minutes",
        icon="mdi:speedometer",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="vigorousIntensityMinutes",
        source="daily_summary",
    ),
)

HEART_RATE_SENSORS: tuple[GarminSensorEntityDescription, ...] = (
    GarminSensorEntityDescription(
        key="resting_heart_rate",
        translation_key="resting_heart_rate",
        name="Resting Heart Rate",
        icon="mdi:heart-pulse",
        native_unit_of_measurement="bpm",
        state_class=SensorStateClass.MEASUREMENT,
        value_key="restingHeartRate",
        source="heart_rate",
    ),
    GarminSensorEntityDescription(
        key="max_heart_rate",
        translation_key="max_heart_rate",
        name="Max Heart Rate",
        icon="mdi:heart-pulse",
        native_unit_of_measurement="bpm",
        state_class=SensorStateClass.MEASUREMENT,
        value_key="maxHeartRate",
        source="heart_rate",
    ),
    GarminSensorEntityDescription(
        key="min_heart_rate",
        translation_key="min_heart_rate",
        name="Min Heart Rate",
        icon="mdi:heart-pulse",
        native_unit_of_measurement="bpm",
        state_class=SensorStateClass.MEASUREMENT,
        value_key="minHeartRate",
        source="heart_rate",
    ),
)

BODY_BATTERY_SENSORS: tuple[GarminSensorEntityDescription, ...] = (
    GarminSensorEntityDescription(
        key="body_battery_most_recent",
        translation_key="body_battery_most_recent",
        name="Body Battery",
        icon="mdi:battery-heart-variant",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="bodyBatteryMostRecentValue",
        source="body_battery",
    ),
    GarminSensorEntityDescription(
        key="body_battery_highest",
        translation_key="body_battery_highest",
        name="Body Battery Highest",
        icon="mdi:battery-heart-variant",
        native_unit_of_measurement=PERCENTAGE,
        value_key="bodyBatteryHighestValue",
        source="body_battery",
    ),
    GarminSensorEntityDescription(
        key="body_battery_lowest",
        translation_key="body_battery_lowest",
        name="Body Battery Lowest",
        icon="mdi:battery-heart-variant",
        native_unit_of_measurement=PERCENTAGE,
        value_key="bodyBatteryLowestValue",
        source="body_battery",
    ),
    GarminSensorEntityDescription(
        key="body_battery_charged",
        translation_key="body_battery_charged",
        name="Body Battery Charged",
        icon="mdi:battery-charging",
        native_unit_of_measurement=PERCENTAGE,
        value_key="bodyBatteryChargedValue",
        source="body_battery",
    ),
    GarminSensorEntityDescription(
        key="body_battery_drained",
        translation_key="body_battery_drained",
        name="Body Battery Drained",
        icon="mdi:battery-arrow-down",
        native_unit_of_measurement=PERCENTAGE,
        value_key="bodyBatteryDrainedValue",
        source="body_battery",
    ),
)

STRESS_SENSORS: tuple[GarminSensorEntityDescription, ...] = (
    GarminSensorEntityDescription(
        key="overall_stress_level",
        translation_key="overall_stress_level",
        name="Overall Stress Level",
        icon="mdi:head-snowflake",
        state_class=SensorStateClass.MEASUREMENT,
        value_key="overallStressLevel",
        source="stress",
    ),
    GarminSensorEntityDescription(
        key="rest_stress_duration",
        translation_key="rest_stress_duration",
        name="Rest Stress Duration",
        icon="mdi:meditation",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_key="restStressDuration",
        source="stress",
    ),
    GarminSensorEntityDescription(
        key="low_stress_duration",
        translation_key="low_stress_duration",
        name="Low Stress Duration",
        icon="mdi:emoticon-happy",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_key="lowStressDuration",
        source="stress",
    ),
    GarminSensorEntityDescription(
        key="medium_stress_duration",
        translation_key="medium_stress_duration",
        name="Medium Stress Duration",
        icon="mdi:emoticon-neutral",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_key="mediumStressDuration",
        source="stress",
    ),
    GarminSensorEntityDescription(
        key="high_stress_duration",
        translation_key="high_stress_duration",
        name="High Stress Duration",
        icon="mdi:emoticon-angry",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_key="highStressDuration",
        source="stress",
    ),
    GarminSensorEntityDescription(
        key="stress_qualifier",
        translation_key="stress_qualifier",
        name="Stress Qualifier",
        icon="mdi:head-snowflake-outline",
        value_key="stressQualifier",
        source="stress",
    ),
)

SLEEP_SENSORS: tuple[GarminSensorEntityDescription, ...] = (
    GarminSensorEntityDescription(
        key="sleep_score",
        translation_key="sleep_score",
        name="Sleep Score",
        icon="mdi:sleep",
        state_class=SensorStateClass.MEASUREMENT,
        value_key="sleepScores.overall.value",
        source="sleep",
    ),
    GarminSensorEntityDescription(
        key="sleep_duration",
        translation_key="sleep_duration",
        name="Sleep Duration",
        icon="mdi:clock-time-eight",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        value_key="sleepTimeSeconds",
        source="sleep",
    ),
    GarminSensorEntityDescription(
        key="deep_sleep",
        translation_key="deep_sleep",
        name="Deep Sleep",
        icon="mdi:power-sleep",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        value_key="deepSleepSeconds",
        source="sleep",
    ),
    GarminSensorEntityDescription(
        key="light_sleep",
        translation_key="light_sleep",
        name="Light Sleep",
        icon="mdi:sleep",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        value_key="lightSleepSeconds",
        source="sleep",
    ),
    GarminSensorEntityDescription(
        key="rem_sleep",
        translation_key="rem_sleep",
        name="REM Sleep",
        icon="mdi:eye-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        value_key="remSleepSeconds",
        source="sleep",
    ),
    GarminSensorEntityDescription(
        key="awake_sleep",
        translation_key="awake_sleep",
        name="Awake Duration",
        icon="mdi:eye",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        value_key="awakeSleepSeconds",
        source="sleep",
    ),
)

SPO2_SENSORS: tuple[GarminSensorEntityDescription, ...] = (
    GarminSensorEntityDescription(
        key="latest_spo2",
        translation_key="latest_spo2",
        name="Latest SpO2",
        icon="mdi:lungs",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="latestSpo2",
        source="spo2",
    ),
    GarminSensorEntityDescription(
        key="lowest_spo2",
        translation_key="lowest_spo2",
        name="Lowest SpO2",
        icon="mdi:lungs",
        native_unit_of_measurement=PERCENTAGE,
        value_key="lowestSpo2",
        source="spo2",
    ),
    GarminSensorEntityDescription(
        key="average_spo2",
        translation_key="average_spo2",
        name="Average SpO2",
        icon="mdi:lungs",
        native_unit_of_measurement=PERCENTAGE,
        value_key="averageSpo2",
        source="spo2",
    ),
)

RESPIRATION_SENSORS: tuple[GarminSensorEntityDescription, ...] = (
    GarminSensorEntityDescription(
        key="avg_waking_respiration",
        translation_key="avg_waking_respiration",
        name="Avg Waking Respiration",
        icon="mdi:weather-windy",
        native_unit_of_measurement="brpm",
        state_class=SensorStateClass.MEASUREMENT,
        value_key="avgWakingRespirationValue",
        source="respiration",
    ),
    GarminSensorEntityDescription(
        key="avg_sleeping_respiration",
        translation_key="avg_sleeping_respiration",
        name="Avg Sleeping Respiration",
        icon="mdi:weather-windy",
        native_unit_of_measurement="brpm",
        state_class=SensorStateClass.MEASUREMENT,
        value_key="avgSleepingRespirationValue",
        source="respiration",
    ),
    GarminSensorEntityDescription(
        key="highest_respiration",
        translation_key="highest_respiration",
        name="Highest Respiration",
        icon="mdi:weather-windy",
        native_unit_of_measurement="brpm",
        value_key="highestRespirationValue",
        source="respiration",
    ),
    GarminSensorEntityDescription(
        key="lowest_respiration",
        translation_key="lowest_respiration",
        name="Lowest Respiration",
        icon="mdi:weather-windy",
        native_unit_of_measurement="brpm",
        value_key="lowestRespirationValue",
        source="respiration",
    ),
)

ADVANCED_SENSORS: tuple[GarminSensorEntityDescription, ...] = (
    GarminSensorEntityDescription(
        key="training_readiness_score",
        translation_key="training_readiness_score",
        name="Training Readiness",
        icon="mdi:weight-lifter",
        state_class=SensorStateClass.MEASUREMENT,
        value_key="score",
        source="training_readiness",
    ),
    GarminSensorEntityDescription(
        key="hrv_weekly_average",
        translation_key="hrv_weekly_average",
        name="HRV Weekly Average",
        icon="mdi:heart-flash",
        native_unit_of_measurement="ms",
        state_class=SensorStateClass.MEASUREMENT,
        value_key="weeklyAvg",
        source="hrv",
    ),
)

LAST_ACTIVITY_SENSORS: tuple[GarminSensorEntityDescription, ...] = (
    GarminSensorEntityDescription(
        key="last_activity_name",
        translation_key="last_activity_name",
        name="Last Activity",
        icon="mdi:run",
        value_key="activityName",
        source="last_activity",
    ),
    GarminSensorEntityDescription(
        key="last_activity_type",
        translation_key="last_activity_type",
        name="Last Activity Type",
        icon="mdi:run",
        value_key="activityType.typeKey",
        source="last_activity",
    ),
    GarminSensorEntityDescription(
        key="last_activity_distance",
        translation_key="last_activity_distance",
        name="Last Activity Distance",
        icon="mdi:map-marker-distance",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.METERS,
        value_key="distance",
        source="last_activity",
    ),
    GarminSensorEntityDescription(
        key="last_activity_duration",
        translation_key="last_activity_duration",
        name="Last Activity Duration",
        icon="mdi:timer",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        value_key="duration",
        source="last_activity",
    ),
    GarminSensorEntityDescription(
        key="last_activity_calories",
        translation_key="last_activity_calories",
        name="Last Activity Calories",
        icon="mdi:fire",
        native_unit_of_measurement="kcal",
        value_key="calories",
        source="last_activity",
    ),
)

ALL_SENSORS: tuple[GarminSensorEntityDescription, ...] = (
    *DAILY_SUMMARY_SENSORS,
    *HEART_RATE_SENSORS,
    *BODY_BATTERY_SENSORS,
    *STRESS_SENSORS,
    *SLEEP_SENSORS,
    *SPO2_SENSORS,
    *RESPIRATION_SENSORS,
    *ADVANCED_SENSORS,
    *LAST_ACTIVITY_SENSORS,
)
