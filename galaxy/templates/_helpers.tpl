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
Decide whether to create a new secret or use an existing secret.
It creates a new secret if the value is the expected default, and assumes it's an
existing secret in all other cases.
*/}}
{{- define "galaxy.createGalaxyDbSecret" -}}
{{- range $key, $entry := .Values.extraEnv -}}
{{- if eq $entry.name "GALAXY_DB_USER_PASSWORD" -}}
    {{- if eq $entry.valueFrom.secretKeyRef.name "{{ .Release.Name }}-galaxy-db-password" -}}
        {{- true -}}
    {{- else -}}
    {{- end -}}
{{- else -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Return galaxy database user password
*/}}
{{- define "galaxy.galaxyDbPassword" -}}
{{- if .Values.postgresql.galaxyDatabasePassword }}
    {{- .Values.postgresql.galaxyDatabasePassword -}}
{{- else -}}
    {{- randAlphaNum 10 -}}
{{- end -}}
{{- end -}}

{{/*
Creates the bash command for the init containers used to place files and change permissions in the galaxy pods
*/}}
{{- define "galaxy.init-container-commands" -}}
{{- tpl "install -o 101 -g 101 /galaxy/server/config/integrated_tool_panel.xml /galaxy/server/config/mutable/integrated_tool_panel.xml; install -o 101 -g 101 /galaxy/server/config/sanitize_whitelist.txt /galaxy/server/config/mutable/sanitize_whitelist.txt; if [ ! -f \"{{ .Values.persistence.mountPath }}/config/editable_shed_tool_conf.xml\" ]; then install -D -o 101 -g 101 /galaxy/server/config/shed_tool_conf.xml.sample {{ .Values.persistence.mountPath }}/config/editable_shed_tool_conf.xml; fi" $}}
{{- end -}}
