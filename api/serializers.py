from rest_framework import serializers
from region.models import Region

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'region_name', 'region_code', 'region_slug', 'region_description']
        read_only_fields = ['id']
    
    def validate_region_name(self, value):
        if not value:
            raise serializers.ValidationError("Region name cannot be empty.")
        return value

    def validate_region_code(self, value):
        if not value:
            raise serializers.ValidationError("Region code cannot be empty.")
        return value