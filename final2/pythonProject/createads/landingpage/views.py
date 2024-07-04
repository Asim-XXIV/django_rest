import logging
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsAdminUser
from .serializers import AdminAdvertisementSerializer

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# Assume 'logs' is the directory where your log file resides
file_handler = logging.FileHandler('logs/debug.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class AdminAdvertisementCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        logger.debug(f"Received POST request data: {request.data}")
        try:
            serializer = AdminAdvertisementSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info("Advertisement created successfully.")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Invalid data: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
