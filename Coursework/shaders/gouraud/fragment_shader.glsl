# version 130 // required to use OpenGL core standard

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 fragment_color;

//=== 'out' attributes are the output image, usually only one for the colour of each pixel
out vec3 final_color;

///=== main shader code
void main() {
      final_color = fragment_color;
}


