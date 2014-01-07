# -*- coding: utf-8 -*-
"""4x4 Matrix which supports rotation, translation, scale and skew.

Matrices are laid out in row-major format and can be loaded directly
into OpenGL.
To convert to column-major format, transpose the array using the
numpy.array.T method.
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import math

import numpy

from pyrr import matrix33
from pyrr.utils import all_parameters_as_numpy_arrays


def create_identity():
    """Creates a new matrix44 and sets it to
    an identity matrix.

    :rtype: numpy.array
    :return: A matrix representing an identity matrix with shape (4,4).
    """
    return numpy.identity( 4, dtype = 'float' )

def create_from_matrix33( mat ):
    """Creates a Matrix44 from a Matrix33.

    The translation will be 0,0,0.

    :rtype: numpy.array
    :return: A matrix with shape (4,4) with the input matrix rotation.
    """
    mat4 = numpy.identity( 4, dtype = 'float' )
    mat4[ 0:3, 0:3 ] = mat
    return mat4

def create_matrix33_view( mat ):
    """Returns a view into the matrix in Matrix33 format.

    This is different from matrix33.create_from_matrix44, in that
    changes to the returned matrix will also alter the original matrix.

    :rtype: numpy.array
    :return: A view into the matrix in the format of a matrix33 (shape (3,3)).
    """
    return mat[ 0:3, 0:3 ]

def create_from_eulers( eulers ):
    """Creates a matrix from the specified Euler rotations.

    :param numpy.array eulers: A set of euler rotations in the format
        specified by the euler modules.
    :rtype: numpy.array
    :return: A matrix with shape (4,4) with the euler's rotation.
    """
    # set to identity matrix
    # this will populate our extra rows for us
    mat = create_identity()
    
    # we'll use Matrix33 for our conversion
    mat33 = matrix33.create_from_eulers( eulers )
    mat[ 0:3, 0:3 ] = mat33
    return mat

def create_from_quaternion( quat ):
    """Creates a matrix with the same rotation as a quaternion.

    :param quat: The quaternion to create the matrix from.
    :rtype: numpy.array
    :return: A matrix with shape (4,4) with the quaternion's rotation.
    """
    # set to identity matrix
    # this will populate our extra rows for us
    mat = create_identity()
    
    # we'll use Matrix33 for our conversion
    mat[ 0:3, 0:3 ] = matrix33.create_from_quaternion( quat )
    return mat

def create_from_inverse_of_quaternion( quat ):
    """Creates a matrix with the inverse rotation of a quaternion.

    This can be used to go from object space to intertial space.

    :param numpy.array quat: The quaternion to make the matrix from (shape 4).
    :rtype: numpy.array
    :return: A matrix with shape (4,4) that respresents the inverse of
        the quaternion.
    """
    # set to identity matrix
    # this will populate our extra rows for us
    mat = create_identity()
    
    # we'll use Matrix33 for our conversion
    mat[ 0:3, 0:3 ] = matrix33.create_from_inverse_of_quaternion( quat )
    return mat

def create_from_translation( vec ):
    """Creates an identity matrix with the translation set.

    :param numpy.array vec: The translation vector (shape 3 or 4).
    :rtype: numpy.array
    :return: A matrix with shape (4,4) that represents a matrix
        with the translation set to the specified vector.
    """
    mat = create_identity()
    mat[ 3, 0:3 ] = vec[:3]
    return mat

def create_from_scale( scale ):
    """Creates an identity matrix with the scale set.

    :param numpy.array scale: The scale to apply as a vector (shape 3).
    :rtype: numpy.array
    :return: A matrix with shape (4,4) with the scale 
        set to the specified vector.
    """
    # we need to expand 'scale' into it's components
    # because numpy isn't flattening them properly.
    return numpy.diagflat(
        [ scale[ 0 ], scale[ 1 ], scale[ 2 ], 1.0 ]
        )

def create_from_x_rotation( theta ):
    """Creates a matrix with the specified rotation about the X axis.

    :param float theta: The rotation, in radians, about the X-axis.
    :rtype: numpy.array
    :return: A matrix with the shape (4,4) with the specified rotation about
        the X-axis.
    
    .. seealso:: http://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions
    """
    mat = create_identity()
    mat[ 0:3, 0:3 ] = matrix33.create_from_x_rotation( theta )
    return mat

def create_from_y_rotation( theta ):
    """Creates a matrix with the specified rotation about the Y axis.

    :param float theta: The rotation, in radians, about the Y-axis.
    :rtype: numpy.array
    :return: A matrix with the shape (4,4) with the specified rotation about
        the Y-axis.
    
    .. seealso:: http://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions
    """
    mat = create_identity()
    mat[ 0:3, 0:3 ] = matrix33.create_from_y_rotation( theta )
    return mat

def create_from_z_rotation( theta ):
    """Creates a matrix with the specified rotation about the Z axis.

    :param float theta: The rotation, in radians, about the Z-axis.
    :rtype: numpy.array
    :return: A matrix with the shape (4,4) with the specified rotation about
        the Z-axis.
    
    .. seealso:: http://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions
    """
    mat = create_identity()
    mat[ 0:3, 0:3 ] = matrix33.create_from_z_rotation( theta )
    return mat

@all_parameters_as_numpy_arrays
def apply_to_vector( mat, vec ):
    """Apply a matrix to a vector.

    The matrix's rotation and translation are applied to the vector.
    Supports multiple matrices and vectors.

    :param numpy.array mat: The rotation / translation matrix.
        Can be a list of matrices.
    :param numpy.array vec: The vector to modify.
        Can be a list of vectors.
    :rtype: numpy.array
    :return: The vectors rotated by the specified matrix.
    """
    if vec.size == 3:
        # convert to a vec4
        vec4 = numpy.array( [ vec[ 0 ], vec[ 1 ], vec[ 2 ], 1.0 ] )
        vec4 = numpy.dot( vec4, mat )

        # handle W value
        if vec4[-1] != 0.0:
            vec4 /= vec4[-1]
        return vec4[:-1]
    elif vec.size == 4:
        return numpy.dot( vec, mat )
    else:
        raise ValueError( "Vector size unsupported" )

def multiply( m1, m2, out = None ):
    """Multiply two matricies, m1 . m2.

    This is essentially a wrapper around
    numpy.dot( m1, m2 )

    :param numpy.array m1: The first matrix.
        Can be a list of matrices.
    :param numpy.array m2: The second matrix.
        Can be a list of matrices.
    :rtype: numpy.array
    :return: A matrix that results from multiplying m1 by m2.
    """
    # using an input as the out value will cause corruption
    if out == m1 or out == m2:
        raise ValueError( "Output must not be one of the inputs, use assignment instead" )

    return numpy.dot( m1, m2, out = out )

def create_perspective_projection_matrix(fovy, aspect, near, far):
    '''
    Creates perspective projection matrix.

    .. seealso:: http://www.opengl.org/sdk/docs/man2/xhtml/gluPerspective.xml

    :param float fovy: field of view in y direction in degrees
    :param float aspect: aspect ratio of the view (width / height)
    :param float near: distance from the viewer to the near clipping plane (only positive)
    :param float far: distance from the viewer to the far clipping plane (only positive)
    :rtype: numpy.array
    :return: A projection matrix representing the specified perpective.
    '''

    f = 1.0 / math.tan(math.radians(fovy / 2.0))
    A = f / aspect
    B = 1.0 * (near + far) / (near - far)
    C = (2.0 * near * far) / (near - far)

    return numpy.array((
        (A, 0, 0, 0),
        (0, f, 0, 0),
        (0, 0, B,-1),
        (0, 0, C, 0)
        ), dtype='float')

def create_perspective_projection_matrix_from_bounds(
    left,
    right,
    top,
    bottom,
    near,
    far
    ):
    """Creates a perspective projection matrix using the specified near
    plane dimensions.

    :param float left: The left of the near plane relative to the plane's centre.
    :param float right: The right of the near plane relative to the plane's centre.
    :param float top: The top of the near plane relative to the plane's centre.
    :param float bottom: The bottom of the near plane relative to the plane's centre.
    :param float near: The distance of the near plane from the camera's origin.
        It is recommended that the near plane is set to 1.0 or above to avoid rendering issues
        at close range.
    :param float far: The distance of the far plane from the camera's origin.
    :rtype: numpy.array
    :return: A projection matrix representing the specified perspective.

    .. seealso:: http://www.gamedev.net/topic/264248-building-a-projection-matrix-without-api/
    .. seealso:: http://www.glprogramming.com/red/chapter03.html
    """

    """
    E  0  A  0
    0  F  B  0
    0  0  C  D
    0  0  -1 0

    A = (right+left)/(right-left)
    B = (top+bottom)/(top-bottom)
    C = -(far+near)/(far-near)
    D = -2*far*near/(far-near)
    E = 2*near/(right-left)
    F = 2*near/(top-bottom)
    """
    A = (right + left) / (right - left)
    B = (top + bottom) / (top - bottom)
    C = -(far + near) / (far - near)
    D = -2.0 * far * near / (far - near)
    E = 2.0 * near / (right - left)
    F = 2.0 * near / (top - bottom)

    return numpy.array(
        [
            [   E, 0.0, 0.0, 0.0 ],
            [ 0.0,   F, 0.0, 0.0 ],
            [   A,   B,   C,-1.0 ],
            [ 0.0, 0.0,   D, 0.0 ],
            ],
            dtype = 'float'
        )

def create_orthogonal_projection_matrix(
    left,
    right,
    top,
    bottom,
    near,
    far
    ):
    """Creates an orthogonal projection matrix.

    :param float left: The left of the near plane relative to the plane's centre.
    :param float right: The right of the near plane relative to the plane's centre.
    :param float top: The top of the near plane relative to the plane's centre.
    :param float bottom: The bottom of the near plane relative to the plane's centre.
    :param float near: The distance of the near plane from the camera's origin.
        It is recommended that the near plane is set to 1.0 or above to avoid rendering issues
        at close range.
    :param float far: The distance of the far plane from the camera's origin.
    :rtype: numpy.array
    :return: A projection matrix representing the specified orthogonal perspective.

    .. seealso:: http://msdn.microsoft.com/en-us/library/dd373965(v=vs.85).aspx
    """

    """
    A 0 0 Tx
    0 B 0 Ty
    0 0 C Tz
    0 0 0 1

    A = 2 / (right - left)
    B = 2 / (top - bottom)
    C = -2 / (far - near)
    """
    A = 2 / (right - left)
    B = 2 / (top - bottom)
    C = -2 / (far - near)

    return numpy.array(
        [
            [   A, 0.0, 0.0, 0.0 ],
            [ 0.0,   B, 0.0, 0.0 ],
            [ 0.0, 0.0,   C, 0.0 ],
            [ 0.0, 0.0, 0.0, 1.0 ],
            ],
            dtype = 'float'
        )

def inverse( m ):
    """Returns the inverse of the matrix.

    This is essentially a wrapper around numpy.linalg.inv.

    :param numpy.array m: A matrix.
    :rtype: numpy.array
    :return: The inverse of the specified matrix.

    .. seealso:: http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.inv.html
    """
    return numpy.linalg.inv( m )
