from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from usuarios.models import UsuarioP

class UserGetSerializer(ModelSerializer):
	class Meta:
		model = UsuarioP
		fields = [
			'nickname',
			'password',
			]
		
class UserGetSerializerC(ModelSerializer):
	class Meta:
		model = UsuarioP
		fields = [
			'nickname',
			'nombre',
			'apellido',
			'password',
			'estado',
			'tipo',
			]