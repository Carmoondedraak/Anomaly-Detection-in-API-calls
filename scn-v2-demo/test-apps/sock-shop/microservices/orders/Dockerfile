FROM maven:3.2-jdk-8 AS build
COPY src /usr/src/app/src
COPY pom.xml /usr/src/app
RUN mvn -f /usr/src/app/pom.xml clean -DskipTests package

FROM openjdk:8-jdk-alpine3.9
COPY --from=build /usr/src/app/target/*.jar /usr/app/app.jar
EXPOSE 8082
ENTRYPOINT ["java","-jar","/usr/app/app.jar"]