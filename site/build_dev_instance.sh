podman build . --tag=letmein-site
if test -f ".env.container"; then
	echo ".env.container already exists. Not creating."
else
	echo "Creating .env.container..."
	cat << EOF > .env.container
LMI_TEMPLATES=/templates/*
LMI_STATIC=/static
LMI_BROKER=
LMI_BROKER_PORT=1883
EOF
fi
