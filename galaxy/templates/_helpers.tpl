{{/*
Expand the name of the chart.
*/}}
{{- define "galaxy.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "galaxy.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "galaxy.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "galaxy.labels" -}}
helm.sh/chart: {{ include "galaxy.chart" . }}
{{ include "galaxy.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "galaxy.selectorLabels" -}}
app.kubernetes.io/name: {{ include "galaxy.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "galaxy.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "galaxy.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Return the postgresql database name to use
*/}}
{{- define "galaxy-postgresql.fullname" -}}
{{- if .Values.postgresql.existingDatabase -}}
{{- printf "%s" .Values.postgresql.existingDatabase -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name .Values.postgresql.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}
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


{{- define "galaxy.operator-user-secret-name" -}}
{{- printf "%s.%s.credentials.postgresql.acid.zalan.do" .Values.postgresql.galaxyDatabaseUser (include "galaxy-postgresql.fullname" .) -}}
{{- end -}}

{{- define "galaxy.galaxy-secret-name" -}}
{{- printf "%s-galaxy-secrets" .Release.Name -}}
{{- end -}}

{{/*
Return galaxy database user password.
Lookup the existing secret values if they exist, or generate a random value
*/}}
{{- define "galaxy.galaxyDbPassword" -}}
{{- $galaxy_secret_name := (include "galaxy.galaxy-secret-name" .) -}}
{{- $galaxy_secret := (lookup "v1" "Secret" .Release.Namespace $galaxy_secret_name) -}}
{{- $operator_secret_name := (include "galaxy.operator-user-secret-name" .) -}}
{{- $operator_secret := (lookup "v1" "Secret" .Release.Namespace $operator_secret_name) -}}
{{- if $galaxy_secret -}}
    {{- $galaxy_key_ref := (default "galaxy-db-password" .Values.postgresql.galaxyExistingSecretKeyRef) -}}
    {{- index $galaxy_secret "data" $galaxy_key_ref | b64dec -}}
{{- else if $operator_secret -}}
    {{- $operator_secret.data.password | b64dec -}}
{{- else if .Values.postgresql.galaxyDatabasePassword -}}
    {{- .Values.postgresql.galaxyDatabasePassword -}}
{{- else -}}
    {{- $randomValue := (randAlphaNum 32) -}}
    {{- $generatedValue := (set .Values.postgresql "galaxyDatabasePassword" $randomValue) -}}
    {{- .Values.postgresql.galaxyDatabasePassword -}}
{{- end -}}
{{- end -}}

{{/*
Creates the bash command for the init containers used to place files and change permissions in the galaxy pods
*/}}
{{- define "galaxy.init-container-commands" -}}
cp -anL /galaxy/server/config/integrated_tool_panel.xml /galaxy/server/config/mutable/integrated_tool_panel.xml;
cp -anL /galaxy/server/config/sanitize_allowlist.txt /galaxy/server/config/mutable/sanitize_allowlist.txt;
cp -anL /galaxy/server/config/data_manager_conf.xml.sample /galaxy/server/config/mutable/shed_data_manager_conf.xml;
cp -anL /galaxy/server/config/tool_data_table_conf.xml.sample /galaxy/server/config/mutable/shed_tool_data_table_conf.xml;
cp -aruL /galaxy/server/tool-data {{.Values.persistence.mountPath}}/;
cp -aruL /galaxy/server/tools {{.Values.persistence.mountPath}}/tools | true;
{{- end -}}

{{/*
Make string DNS-compliant by turning to lowercase then removing all noncompliant characters
*/}}
{{- define "galaxy.makeDnsCompliant" -}}
{{- (printf "%s" (regexReplaceAll "[^a-z0-9-]" (. | lower) "")) | trunc 63 | trimSuffix "-"  }}
{{- end -}}

{{/*
Get unique name for extra files
*/}}
{{- define "galaxy.getExtraFilesUniqueName" -}}
{{- (printf "%s" (include "galaxy.makeDnsCompliant" (printf "extra-%s-%s" (include "galaxy.getFilenameFromPath" .) (. | sha256sum))))  }}
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
              value: postgresql://{{ .Values.postgresql.galaxyDatabaseUser }}:$(GALAXY_DB_USER_PASSWORD)@{{ template "galaxy-postgresql.fullname" . }}/galaxy{{- if not (or .Values.postgresql.enabled .Values.postgresql.existingDatabase) -}}?sslmode=require{{- end }}
            - name: GALAXY_CONFIG_OVERRIDE_ID_SECRET
              valueFrom:
                secretKeyRef:
                  name: "{{ .Release.Name }}-galaxy-secrets"
                  key: "galaxy-config-id-secret"
{{- end -}}

{{/*
Define pod priority class
*/}}
{{- define "galaxy.pod-priority-class" -}}
{{- if .Values.jobHandlers.priorityClass.existingClass -}}
{{- printf "%s" .Values.jobHandlers.priorityClass.existingClass -}}
{{- else -}}
{{- printf "%s-job-priority" (include "galaxy.fullname" .) -}}
{{- end -}}
{{- end -}}

{{/*
Define extra persistent volumes
*/}}
{{- define "galaxy.extra_pvc_mounts" -}}
  {{- if .Values.extraVolumes }}
    {{- range $num, $entry := .Values.extraVolumes }}
      {{- if $entry.name }}
        {{- if $entry.persistentVolumeClaim}}
          {{- if $entry.persistentVolumeClaim.claimName }}
            {{- range $num, $mount := $.Values.extraVolumeMounts }}
              {{- if $mount.name }}
                {{- if (eq $entry.name $mount.name) }}
                  {{- if $mount.mountPath -}}
                    ,{{- $entry.persistentVolumeClaim.claimName -}}:{{- $mount.mountPath -}}
                  {{- end }}
                {{- end }}
              {{- end }}
            {{- end }}
          {{- end }}
        {{- end }}
      {{- end }}
    {{- end }}
  {{- end -}}
{{- end -}}
