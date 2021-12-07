# prometheus-webhook-dingtalk
> prometheus告警推送到钉钉机器人

## 创建钉钉机器人

这里就不在BB了，官方文档有详细说明:[添加机器人到钉钉群 - 钉钉开放平台 (dingtalk.com)](https://developers.dingtalk.com/document/robots/use-group-robots)

*`注意新版的钉钉机器人必需选择安全设置`*

- 本文选用`加签` 等会需要用到

##  配置secret资源

```bash
$ kubectl create secret generic dingtalk-secret --from-literal=token=<替换webhook-token> --from-literal=secret=<替换加签秘钥SEC开头> -n monitoring
```

##  创建deployment文件

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: webhook-dingtalk
  name: webhook-dingtalk
  namespace: monitoring
  #需要和alertmanager在同一个namespace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: webhook-dingtalk
  template:
    metadata:
      labels:
        app: webhook-dingtalk
    spec:
      containers:
      - image: uhub.service.ucloud.cn/jackhe/prometheus-webhook-dingtalk:v1.1
        name: webhook-dingtalk
        ports:
        - containerPort: 8080
          protocol: TCP
        env:
        - name: ROBOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: dingtalk-secret
              key: token
        - name: ROBOT_SECRET
          valueFrom:
            secretKeyRef:
              name: dingtalk-secret
              key: secret
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
          limits:
            cpu: 500m
            memory: 500Mi
        livenessProbe:
          failureThreshold: 3
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          timeoutSeconds: 1
          tcpSocket:
            port: 8080
        readinessProbe:
          failureThreshold: 3
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          timeoutSeconds: 1
          httpGet:
            port: 8080
            path: /
      imagePullSecrets:
        - name: IfNotPresent
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: webhook-dingtalk
  name: webhook-dingtalk
  namespace: monitoring
  #需要和alertmanager在同一个namespace
spec:
  ports:
  - name: http
    port: 80
    protocol: TCP
    targetPort: 8080
  selector:
    app: webhook-dingtalk
  type: ClusterIP
```

##  alertmanager添加webhook告警路由

```
route:
  receiver: webhook
receivers:
- name: webhook
   webhook_configs:
   - url: http://webhook-dingtalk/dingtalk/send/
```

