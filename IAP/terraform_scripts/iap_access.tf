resource "google_iap_web_iam_binding" "binding" {
  project = var.gcp_project_id
  role = "roles/iap.httpsResourceAccessor"
  members = [ for user in var.users : "user:${user}" ]
}