from wbgps import *
from pyspark import StorageLevel
import pyspark.sql.functions as F
from pyspark.sql.functions import pandas_udf, PandasUDFType, col, lit, lag, countDistinct, to_timestamp
from pyspark.sql.types import StructType, StructField, LongType, StringType, IntegerType, TimestampType, DoubleType
from pyspark.sql.window import Window
from pyspark.sql.functions import udf
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

results_path_spark = f"/mnt/Geospatial/results/veraset/{c.country}/accuracy100_maxtimestop3600_staytime300_radius50_dbscanradius50/date{c.end_date}/"
df = spark.read.parquet(os.path.join(c.results_path_spark, 'stops_geocoded'))

df = df.withColumn("t_start_hour", F.hour(F.to_timestamp("t_start"))).withColumn("t_end_hour", F.hour(F.to_timestamp("t_end"))).withColumn(
    'weekday', F.dayofweek(F.to_timestamp("t_start"))).withColumn("date", F.to_timestamp("t_start")).withColumn("date_trunc", F.date_trunc("day", F.col("date")))

df = df.withColumnRenamed(
    'latitude', 'lat').withColumnRenamed('longitude', 'lon')

schema_df = StructType([
    StructField('user_id', StringType(), False),
    StructField('t_start', LongType(), False),
    StructField('t_end', LongType(), False),
    StructField('duration', LongType(), False),
    StructField('lat', DoubleType(), False),
    StructField('lon', DoubleType(), False),
    StructField('total_duration_stop_location', LongType(), False),
    StructField('total_pings_stop', LongType(), False),
    StructField('cluster_label', LongType(), False),
    StructField('median_accuracy', DoubleType(), False),
    StructField('location_type', StringType(), True),
    StructField('home_label', LongType(), True),
    StructField('work_label', LongType(), True),
    StructField('geom_id', StringType(), False),
    StructField('date', TimestampType(), True),
    StructField('t_start_hour', IntegerType(), True),
    StructField('t_end_hour', IntegerType(), True),
    StructField("date_trunc", TimestampType(), True)
])
res_df = df.groupBy("user_id").apply(compute_home_work_label_dynamic)

fname = f"personal_stop_location_{c.suffix}"
res_df.write.mode("overwrite").parquet(
    os.path.join(c.results_path_spark, fname))

fname = f"personal_stop_location_{c.suffix}"
res_df = spark.read.parquet(os.path.join(c.results_path_spark, fname))

fname = f"durations_window_{c.suffix}"
res = get_durations(res_df)
res.write.mode("overwrite").parquet(os.path.join(c.results_path_spark, fname))
