from .TableWrapper import TableWrapper


class Particles(TableWrapper):
    def cross_clean(self, others, delta_r=0.4):
        eta_combs = self.eta.cross(others.eta, nested=True)
        phi_combs = self.phi.cross(others.phi, nested=True)

        mask = ~((phi_combs.i1 - phi_combs.i0) ** 2 + (eta_combs.i1 - eta_combs.i0) ** 2 < delta_r ** 2).any()

        return self[mask]
