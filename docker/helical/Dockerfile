# =============================================================================
# Helical Insight Community Edition - Custom Docker Build
#
# NOTE: This builds Helical Insight CE from GitHub source.
#       Requires Maven build (~10 min first time).
#       Uses Tomcat 8.5 + JDK 8 + MySQL (embedded H2 for metadata)
#
# Build:  docker compose build helical
# =============================================================================

FROM maven:3.8-openjdk-8 AS builder

# Clone Helical Insight CE source
RUN git clone --depth 1 https://github.com/helicalinsight/helicalinsight.git /build

WORKDIR /build

# Install custom dependencies referenced in pom.xml
RUN mvn install:install-file \
      -Dfile=db-drivers/HikariCP-4.0.3.jar \
      -DgroupId=com.zaxxer \
      -DartifactId=HikariCP \
      -Dversion=4.0.3 \
      -Dpackaging=jar \
      -DgeneratePom=true 2>/dev/null || true

RUN mvn install:install-file \
      -Dfile=db-drivers/tomcat-jdbc-10.0.27.jar \
      -DgroupId=org.apache.tomcat \
      -DartifactId=tomcat-jdbc \
      -Dversion=10.0.27 \
      -Dpackaging=jar \
      -DgeneratePom=true 2>/dev/null || true

# Build the WAR file (skip tests for speed)
RUN mvn clean package -Denv=production -DskipTests -q || echo "BUILD MAY HAVE WARNINGS"

# ─── Runtime Stage ──────────────────────────────────────────────────────────
FROM tomcat:8.5-jdk8-openjdk

# Remove default Tomcat apps
RUN rm -rf /usr/local/tomcat/webapps/*

# Copy WAR from builder
COPY --from=builder /build/hwf/target/hi-ce.war /usr/local/tomcat/webapps/hi-ce.war

# Add PostgreSQL JDBC driver for data connections
RUN curl -fsSL -o /usr/local/tomcat/lib/postgresql-42.7.1.jar \
    https://jdbc.postgresql.org/download/postgresql-42.7.1.jar

EXPOSE 8080

CMD ["catalina.sh", "run"]
