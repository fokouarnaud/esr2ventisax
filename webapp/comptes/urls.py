from django.contrib.auth import views as auth
from django.urls import path, reverse_lazy

from . import views
from .connexion import FormulaireConnexion, FormulaireMotDePasseOublie, FormulaireNouveauMotDePasse

app_name = "comptes"

urlpatterns = [
    path("connexion/", auth.LoginView.as_view(
        template_name="comptes/connexion.html", authentication_form=FormulaireConnexion,
        redirect_authenticated_user=True), name="connexion"),
    path("deconnexion/", auth.LogoutView.as_view(), name="deconnexion"),
    path("mot-de-passe/", auth.PasswordResetView.as_view(
        template_name="comptes/mdp_oublie.html", form_class=FormulaireMotDePasseOublie,
        email_template_name="comptes/email/mdp_oublie.txt", subject_template_name="comptes/email/mdp_oublie_objet.txt",
        success_url=reverse_lazy("comptes:mdp_envoye")), name="mdp_oublie"),
    path("mot-de-passe/envoye/", auth.PasswordResetDoneView.as_view(
        template_name="comptes/mdp_envoye.html"), name="mdp_envoye"),
    path("mot-de-passe/<uidb64>/<token>/", auth.PasswordResetConfirmView.as_view(
        template_name="comptes/mdp_nouveau.html", form_class=FormulaireNouveauMotDePasse, success_url=reverse_lazy("comptes:mdp_termine")),
        name="mdp_nouveau"),
    path("mot-de-passe/termine/", auth.PasswordResetCompleteView.as_view(
        template_name="comptes/mdp_termine.html"), name="mdp_termine"),
    path("inscription/", views.inscription, name="inscription"),
    path("inscription/envoye/", views.inscription_envoyee, name="inscription_envoyee"),
    path("inscription/verifier/<uidb64>/<jeton>/", views.verifier, name="verifier"),
]
