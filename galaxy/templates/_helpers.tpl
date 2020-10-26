{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "galaxy.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "galaxy.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "galaxy.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}


{{/*
Expand the name of the chart.
*/}}
{{- define "galaxy-postgresql.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.postgresql.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Add a trailing slash to a given path, if missing
*/}}
{{- define "galaxy.add_trailing_slash" -}}
{{- if hasSuffix "/" . -}}
{{- printf "%s" . -}}
{{- else -}}
{{- printf "%s/" . -}}
{{- end -}}
{{- end -}}

{{/*
Return which PVC to use
*/}}
{{- define "galaxy.pvcname" -}}
{{- if .Values.persistence.existingClaim -}}
{{- printf "%s" .Values.persistence.existingClaim -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name .Values.persistence.name -}}
{{- end -}}
{{- end -}}

{{/*
Return galaxy database user password
*/}}
{{- define "galaxy.galaxyDbPassword" -}}
{{- if .Values.postgresql.galaxyDatabasePassword }}
    {{- .Values.postgresql.galaxyDatabasePassword -}}
{{- else -}}
    {{- randAlphaNum 16 -}}
{{- end -}}
{{- end -}}

{{/*
Creates the bash command for the init containers used to place files and change permissions in the galaxy pods
*/}}
{{- define "galaxy.init-container-commands" -}}
cp -anL /galaxy/server/config/integrated_tool_panel.xml /galaxy/server/config/mutable/integrated_tool_panel.xml;
cp -anL /galaxy/server/config/sanitize_whitelist.txt /galaxy/server/config/mutable/sanitize_whitelist.txt;
cp -anL /galaxy/server/config/data_manager_conf.xml.sample /galaxy/server/config/mutable/shed_data_manager_conf.xml;
cp -anL /galaxy/server/config/tool_data_table_conf.xml.sample /galaxy/server/config/mutable/shed_tool_data_table_conf.xml;
cp -aruL /galaxy/server/tool-data {{.Values.persistence.mountPath}}/;
cp -aruL /galaxy/server/tools {{.Values.persistence.mountPath}}/tools | true;
{{- end -}}

{{/*
Extract the filename portion from a file path
*/}}
{{- define "galaxy.getFilenameFromPath" -}}
{{- printf "%s" (. | splitList "/" | last) -}}
{{- end -}}

{{/*
Define pod env vars
*/}}
{{- define "galaxy.podEnvVars" -}}
{{- if .Values.extraEnv }}
{{ tpl (toYaml .Values.extraEnv) . | indent 12 }}
{{- end }}
            - name: GALAXY_DB_USER_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: '{{default (printf "%s-galaxy-secrets" .Release.Name) .Values.postgresql.galaxyExistingSecret}}'
                  key: '{{default "galaxy-db-password" .Values.postgresql.galaxyExistingSecretKeyRef}}'
            - name: GALAXY_CONFIG_OVERRIDE_DATABASE_CONNECTION
              value: postgresql://{{ .Values.postgresql.galaxyDatabaseUser }}:$(GALAXY_DB_USER_PASSWORD)@{{ template "galaxy-postgresql.fullname" . }}/galaxy
            - name: GALAXY_CONFIG_OVERRIDE_ID_SECRET
              valueFrom:
                secretKeyRef:
                  name: "{{ .Release.Name }}-galaxy-secrets"
                  key: "galaxy-config-id-secret"
{{- end -}}
