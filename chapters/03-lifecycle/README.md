# 第3章：生命周期管理

## 本章定位

本章讨论有状态软件如何启动、恢复、关闭和交还资源。重点不是罗列启动步骤，而是对比 Redis、MySQL、Kafka 在状态恢复、事务承诺、集群职责上的不同边界。

## 文件说明

- 正文：`chapter.md`
- 大纲：`outline.md`
- 图示：`diagrams/fig-2-1.svg` 至 `diagrams/fig-2-6.svg`

## 终校关注

- 核对 Redis 7.x 多部 AOF、MySQL `innodb_fast_shutdown`、Kafka 受控关闭的版本口径。
- 检查表 3-1、表 3-2 与正文解读是否互相支撑。
