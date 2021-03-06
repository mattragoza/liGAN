import numpy as np


class AtomGrid(object):
    '''
    An atomic density grid.
    '''
    def __init__(self, values, channels, center, resolution, **info):

        if len(values.shape) != 4:
            raise ValueError('AtomGrid values must have 4 dims')

        if values.shape[0] != len(channels):
            raise ValueError('AtomGrid values have wrong number of channels')

        if not (values.shape[1] == values.shape[2] == values.shape[3]):
            raise ValueError('last 3 dims of AtomGrid values must be equal')

        self.values = values
        self.channels = channels
        self.center = center
        self.resolution = resolution
        self.size = self.values.shape[1]
        self.dimension = self.compute_dimension(self.size, resolution)

        self.info = info

    @classmethod
    def compute_dimension(cls, size, resolution):
        return (size - 1) * resolution

    @classmethod
    def compute_size(cls, dimension, resolution):
        return int(np.ceil(dimension / resolution + 1))

    def to_dx(self, dx_prefix, center=None):
        write_grids_to_dx_files(
            out_prefix=dx_prefix,
            grids=self.values,
            channels=self.channels,
            center=self.center if center is None else center,
            resolution=self.resolution)

    def new_like(self, values, **info):
        '''
        Return a AtomGrid with the same grid settings but new values.
        '''
        return AtomGrid(
            values, self.channels, self.center, self.resolution, **info
        )



def write_grid_to_dx_file(dx_file, grid, center, resolution):
    '''
    Write a grid with a center and resolution to a .dx file.
    '''
    if len(grid.shape) != 3 or len(set(grid.shape)) != 1:
        raise ValueError('grid must have three equal dimensions')
    if len(center) != 3:
        raise ValueError('center must be a vector of length 3')
    dim = grid.shape[0]
    origin = np.array(center) - resolution*(dim-1)/2.
    with open(dx_file, 'w') as f:
        f.write('object 1 class gridpositions counts {:d} {:d} {:d}\n'.format(dim, dim, dim))
        f.write('origin {:.5f} {:.5f} {:.5f}\n'.format(*origin))
        f.write('delta {:.5f} 0 0\n'.format(resolution))
        f.write('delta 0 {:.5f} 0\n'.format(resolution))
        f.write('delta 0 0 {:.5f}\n'.format(resolution))
        f.write('object 2 class gridconnections counts {:d} {:d} {:d}\n'.format(dim, dim, dim))
        f.write('object 3 class array type double rank 0 items [ {:d} ] data follows\n'.format(dim**3))
        total = 0
        for i in range(dim):
            for j in range(dim):
                for k in range(dim):
                    f.write('{:.10f}'.format(grid[i][j][k]))
                    total += 1
                    if total % 3 == 0:
                        f.write('\n')
                    else:
                        f.write(' ')


def write_grids_to_dx_files(out_prefix, grids, channels, center, resolution):
    '''
    Write each of a list of grids a separate .dx file, using the channel names.
    '''
    dx_files = []
    for grid, channel in zip(grids, channels):
        dx_file = '{}_{}.dx'.format(out_prefix, channel.name)
        write_grid_to_dx_file(dx_file, grid, center, resolution)
        dx_files.append(dx_file)
    return dx_files
