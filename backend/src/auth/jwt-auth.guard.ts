import {
    CanActivate,
    ExecutionContext,
    Injectable,
    UnauthorizedException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class JwtAuthGuard implements CanActivate {
    constructor(
        private readonly jwt: JwtService,
    ) {}

    canActivate(
        context: ExecutionContext,
    ): boolean {
        const request = context
            .switchToHttp()
            .getRequest();

        const header = request.headers.authorization;

        if (!header?.startsWith('Bearer ')) {
            throw new UnauthorizedException(
                'Authentication required',
            );
        }

        const token = header.slice(7);

        try {
            request.user = this.jwt.verify(token);
            return true;
        } catch {
            throw new UnauthorizedException(
                'Invalid or expired token',
            );
        }
    }
}
